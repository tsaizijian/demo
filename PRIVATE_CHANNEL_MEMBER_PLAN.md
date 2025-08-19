# 私人頻道成員管理功能設計規劃

## 📋 概述

本文檔規劃私人頻道的成員邀請、管理和權限控制功能，讓私人頻道可以邀請特定用戶加入，並提供完整的成員管理機制。

## 🎯 功能目標

1. **成員邀請**: 頻道創建者/管理員可以邀請用戶加入私人頻道
2. **成員管理**: 查看、移除頻道成員，設定成員角色
3. **權限控制**: 基於角色的頻道訪問與操作權限
4. **即時通知**: WebSocket 通知邀請、加入、離開等事件
5. **用戶體驗**: 直觀的邀請流程和成員管理界面

## 🗄️ 資料庫架構設計

### 1. 新增資料模型

#### ChannelMember (頻道成員關係)

```python
class ChannelMember(AuditMixin, Model):
    """頻道成員關係模型"""
    __tablename__ = 'channel_members'

    id = Column(Integer, primary_key=True)

    # 關聯關係
    channel_id = Column(Integer, ForeignKey('chat_channels.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('ab_user.id'), nullable=False)

    # 關聯對象
    channel = relationship("ChatChannel", backref="members")
    user = relationship("User", backref="channel_memberships")

    # 成員角色
    role = Column(String(20), default='member', comment='成員角色: owner, admin, member')

    # 加入狀態
    status = Column(String(20), default='active', comment='成員狀態: active, invited, banned, left')


    # 索引優化
    __table_args__ = (
        # 確保同一用戶在同一頻道只有一個有效記錄
        Index('idx_channel_user_unique', 'channel_id', 'user_id'),
        Index('idx_channel_members_status', 'channel_id', 'status'),
        Index('idx_user_channels', 'user_id', 'status'),
    )
```

#### ChannelMember 簡化邀請處理

### 2. 修改現有模型

#### ChatChannel 新增欄位

```python
# 在 ChatChannel 模型中新增
member_count = Column(Integer, default=0, comment='成員數量 - 自動同步更新')

# 🆕 頻道密碼功能
join_password = Column(String(255), nullable=True, comment='頻道加入密碼 (bcrypt 加密)')
password_required = Column(Boolean, default=False, comment='是否需要密碼才能加入')
allow_join_by_id = Column(Boolean, default=False, comment='是否允許通過頻道ID直接加入')

# 成員數量同步更新方法
def update_member_count(self):
    """更新成員數量"""
    from sqlalchemy import func
    self.member_count = db.session.query(func.count(ChannelMember.id))\
        .filter_by(channel_id=self.id, status='active').scalar()
    db.session.commit()
```

## 🔌 後端 API 設計

### 1. 成員數量同步 Hook 系統

#### SQLAlchemy 事件監聽器

```python
from sqlalchemy import event
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# 🔄 成員變更時自動更新數量
@event.listens_for(ChannelMember, 'after_insert')
@event.listens_for(ChannelMember, 'after_update')
@event.listens_for(ChannelMember, 'after_delete')
def update_channel_member_count(mapper, connection, target):
    """成員變更時自動更新頻道成員數量"""
    if hasattr(target, 'channel_id'):
        # 使用原始 SQL 避免 ORM 會話問題
        count_query = """
            SELECT COUNT(*) FROM channel_members
            WHERE channel_id = :channel_id AND status = 'active'
        """
        result = connection.execute(
            text(count_query),
            {'channel_id': target.channel_id}
        ).scalar()

        # 更新頻道成員數量
        update_query = """
            UPDATE chat_channels
            SET member_count = :count, changed_on = NOW()
            WHERE id = :channel_id
        """
        connection.execute(
            text(update_query),
            {'count': result, 'channel_id': target.channel_id}
        )

# 密碼加密 Hook
@event.listens_for(ChatChannel.join_password, 'set', retval=True)
def hash_password(target, value, oldvalue, initiator):
    """密碼設定時自動加密"""
    if value and value != oldvalue:
        return bcrypt.generate_password_hash(value).decode('utf-8')
    return value
```

### 2. 頻道成員管理 API

#### `ChannelMemberApi` 類別

```python
class ChannelMemberApi(ModelRestApi):
    """頻道成員管理 API"""
    datamodel = SQLAInterface(ChannelMember)

    # 端點設計
    @expose('/channel/<int:channel_id>/members')
    @jwt_required
    def get_channel_members(self, channel_id):
        """獲取頻道成員列表"""

    @expose('/join-by-id', methods=['POST'])
    @jwt_required
    def join_channel_by_id(self):
        """通過頻道ID和密碼加入頻道"""
        data = request.get_json()
        channel_id = data.get('channel_id')
        password = data.get('password', '')

        # 驗證頻道和密碼
        channel = db.session.query(ChatChannel).filter_by(
            id=channel_id,
            allow_join_by_id=True
        ).first()

        if not channel:
            return jsonify({'error': '頻道不存在或不允許加入'}), 404

        # 檢查密碼
        if channel.password_required:
            if not password or not bcrypt.check_password_hash(channel.join_password, password):
                return jsonify({'error': '密碼錯誤'}), 401

        # 🛡️ 防重入：檢查是否已經是 active 成員
        existing_member = db.session.query(ChannelMember).filter_by(
            channel_id=channel_id,
            user_id=g.user.id,
            status='active'
        ).first()

        if existing_member:
            return jsonify({'error': '您已經是此頻道的成員'}), 400

        # 檢查是否有 pending/invited 狀態的記錄，若有則更新為 active
        pending_member = db.session.query(ChannelMember).filter_by(
            channel_id=channel_id,
            user_id=g.user.id
        ).filter(ChannelMember.status.in_(['invited', 'left'])).first()

        if pending_member:
            # 重新激活現有記錄
            pending_member.status = 'active'
            pending_member.joined_at = datetime.utcnow()
            pending_member.left_at = None
            db.session.commit()

            return jsonify({
                'success': True,
                'message': '成功重新加入頻道',
                'data': {
                    'channel': channel.to_dict(),
                    'member': pending_member.to_dict()
                }
            })

        # 加入頻道
        member = ChannelMember(
            channel_id=channel_id,
            user_id=g.user.id,
            role='member',
            status='active',
            joined_at=datetime.utcnow()
        )
        db.session.add(member)
        db.session.commit()

        # 成員數量會通過 Hook 自動更新

        return jsonify({
            'success': True,
            'message': '成功加入頻道',
            'data': {
                'channel': channel.to_dict(),
                'member': member.to_dict()
            }
        })

    @expose('/channel/<int:channel_id>/leave', methods=['POST'])
    @jwt_required
    def leave_channel(self, channel_id):
        """離開頻道"""
        member = db.session.query(ChannelMember).filter_by(
            channel_id=channel_id,
            user_id=g.user.id,
            status='active'
        ).first()

        if not member:
            return jsonify({'error': '您不是此頻道的成員'}), 400

        # 🛡️ Owner 風險控制：檢查是否需要轉移擁有權
        if member.role == 'owner':
            # 檢查頻道是否還有其他 active 成員
            other_members = db.session.query(ChannelMember).filter_by(
                channel_id=channel_id,
                status='active'
            ).filter(ChannelMember.user_id != g.user.id).all()

            if not other_members:
                # 沒有其他成員，可以直接離開（頻道會變成空的）
                pass
            else:
                # 有其他成員，需要轉移擁有權
                return jsonify({
                    'error': '頻道創建者需要先轉移擁有權才能離開',
                    'transfer_required': True,
                    'available_members': [
                        {
                            'user_id': m.user_id,
                            'username': m.user.username,
                            'display_name': getattr(m.user.profile, 'display_name', m.user.username) if hasattr(m.user, 'profile') else m.user.username,
                            'role': m.role
                        } for m in other_members
                    ]
                }), 400

        # 更新成員狀態為離開
        member.status = 'left'
        member.left_at = datetime.utcnow()
        db.session.commit()

        # 成員數量會通過 Hook 自動更新

        return jsonify({'success': True, 'message': '成功離開頻道'})

    @expose('/channel/<int:channel_id>/remove/<int:user_id>', methods=['POST'])
    @jwt_required
    def remove_member(self, channel_id, user_id):
        """移除頻道成員"""
        # 權限檢查
        current_member = db.session.query(ChannelMember).filter_by(
            channel_id=channel_id,
            user_id=g.user.id,
            status='active'
        ).first()

        if not current_member or current_member.role not in ['owner', 'admin']:
            return jsonify({'error': '權限不足'}), 403

        # 找到要移除的成員
        target_member = db.session.query(ChannelMember).filter_by(
            channel_id=channel_id,
            user_id=user_id,
            status='active'
        ).first()

        if not target_member:
            return jsonify({'error': '成員不存在'}), 404

        if target_member.role == 'owner':
            return jsonify({'error': '無法移除頻道創建者'}), 403

        # 移除成員
        target_member.status = 'banned'
        target_member.left_at = datetime.utcnow()
        db.session.commit()

        # 成員數量會通過 Hook 自動更新

        return jsonify({'success': True, 'message': '成功移除成員'})

    @expose('/channel/<int:channel_id>/transfer-ownership/<int:new_owner_id>', methods=['POST'])
    @jwt_required
    def transfer_ownership(self, channel_id, new_owner_id):
        """🔄 轉移頻道擁有權"""
        # 檢查當前用戶是否為 Owner
        current_member = db.session.query(ChannelMember).filter_by(
            channel_id=channel_id,
            user_id=g.user.id,
            status='active',
            role='owner'
        ).first()

        if not current_member:
            return jsonify({'error': '只有頻道創建者可以轉移擁有權'}), 403

        # 檢查新 Owner 是否為有效成員
        new_owner_member = db.session.query(ChannelMember).filter_by(
            channel_id=channel_id,
            user_id=new_owner_id,
            status='active'
        ).first()

        if not new_owner_member:
            return jsonify({'error': '目標用戶不是此頻道的成員'}), 404

        if new_owner_member.user_id == g.user.id:
            return jsonify({'error': '不能轉移給自己'}), 400

        # 執行轉移
        try:
            # 原 Owner 變成 Admin
            current_member.role = 'admin'

            # 新成員變成 Owner
            new_owner_member.role = 'owner'

            # 更新頻道的 creator_id
            channel = db.session.query(ChatChannel).filter_by(id=channel_id).first()
            if channel:
                channel.creator_id = new_owner_id
                channel.changed_on = datetime.utcnow()
                channel.changed_by_fk = g.user.id

            db.session.commit()

            return jsonify({
                'success': True,
                'message': f'成功轉移頻道擁有權給 {new_owner_member.user.username}',
                'data': {
                    'new_owner': new_owner_member.to_dict(),
                    'former_owner': current_member.to_dict()
                }
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'轉移失敗: {str(e)}'}), 500
```

### 3. API 端點規格

#### POST `/api/v1/channelmemberapi/join-by-id`

**通過頻道 ID 和密碼加入頻道**

請求參數:

```json
{
  "channel_id": 123,
  "password": "mypassword123"
}
```

回應:

```json
{
  "success": true,
  "message": "成功加入頻道",
  "data": {
    "channel": {
      "id": 123,
      "name": "私人討論區",
      "description": "團隊內部討論",
      "member_count": 5
    },
    "member": {
      "role": "member",
      "joined_at": "2024-08-18T10:30:00Z"
    }
  }
}
```

#### POST `/api/v1/channelmemberapi/channel/{channel_id}/transfer-ownership/{new_owner_id}`

**轉移頻道擁有權**

回應:

```json
{
  "success": true,
  "message": "成功轉移頻道擁有權給 alice",
  "data": {
    "new_owner": {
      "user_id": 10,
      "username": "alice",
      "role": "owner"
    },
    "former_owner": {
      "user_id": 5,
      "username": "bob",
      "role": "admin"
    }
  }
}
```

#### GET `/api/v1/channelmemberapi/channel/{channel_id}/members`

**獲取頻道成員**

回應:

```json
{
  "result": [
    {
      "id": 1,
      "user_id": 10,
      "username": "alice",
      "display_name": "Alice Chen",
      "role": "owner",
      "status": "active",
      "joined_at": "2024-08-01T10:00:00Z",
      "avatar_url": null
    }
  ]
}
```

## 🎨 前端 UI/UX 設計

### 1. 成員管理界面

#### 頻道成員側邊欄 (`ChannelMembersSidebar.vue`)

```vue
<template>
  <div class="channel-members-sidebar">
    <!-- 成員列表標題 -->
    <div class="members-header">
      <h3>成員 ({{ members.length }})</h3>
      <Button
        v-if="canInviteMembers"
        icon="pi pi-user-plus"
        @click="showInviteDialog = true"
      />
    </div>

    <!-- 成員列表 -->
    <div class="members-list">
      <div v-for="member in members" :key="member.id" class="member-item">
        <Avatar :label="member.display_name[0]" />
        <div class="member-info">
          <span class="member-name">{{ member.display_name }}</span>
          <Badge :value="member.role" />
        </div>
        <Button
          v-if="canManageMember(member)"
          icon="pi pi-ellipsis-v"
          @click="showMemberActions(member)"
        />
      </div>
    </div>
  </div>
</template>
```

#### 加入頻道對話框 (`JoinChannelDialog.vue`)

```vue
<template>
  <Dialog v-model:visible="visible" header="加入頻道">
    <!-- 頻道ID輸入 -->
    <div class="channel-id-input">
      <FloatLabel>
        <InputText
          id="channelId"
          v-model="channelId"
          placeholder="輸入頻道ID"
        />
        <label for="channelId">頻道 ID</label>
      </FloatLabel>
    </div>

    <!-- 密碼輸入 -->
    <div class="password-input">
      <FloatLabel>
        <Password
          id="password"
          v-model="password"
          placeholder="輸入頻道密碼"
          :feedback="false"
          toggleMask
        />
        <label for="password">頻道密碼</label>
      </FloatLabel>
    </div>

    <!-- 錯誤訊息 -->
    <Message v-if="error" severity="error" :closable="false">
      {{ error }}
    </Message>

    <!-- 操作按鈕 -->
    <template #footer>
      <Button label="取消" @click="visible = false" />
      <Button
        label="加入頻道"
        @click="joinChannelById"
        :loading="loading"
        :disabled="!channelId"
      />
    </template>
  </Dialog>
</template>
```

#### 轉移擁有權對話框 (`TransferOwnershipDialog.vue`)

```vue
<template>
  <Dialog v-model:visible="visible" header="轉移頻道擁有權">
    <!-- 警告訊息 -->
    <Message severity="warn" :closable="false">
      轉移後您將失去頻道擁有權，此操作無法撤銷！
    </Message>

    <!-- 選擇新的擁有者 -->
    <div class="new-owner-selection">
      <h4>選擇新的頻道擁有者</h4>
      <div class="members-list">
        <div
          v-for="member in availableMembers"
          :key="member.user_id"
          class="member-option"
          :class="{ selected: selectedMemberId === member.user_id }"
          @click="selectedMemberId = member.user_id"
        >
          <Avatar :label="member.display_name[0]" />
          <div class="member-info">
            <span class="member-name">{{ member.display_name }}</span>
            <Badge :value="member.role" />
          </div>
          <RadioButton :value="member.user_id" v-model="selectedMemberId" />
        </div>
      </div>
    </div>

    <!-- 確認輸入 -->
    <div class="confirmation-input">
      <FloatLabel>
        <InputText
          id="confirmText"
          v-model="confirmText"
          placeholder="請輸入 '轉移擁有權' 來確認"
        />
        <label for="confirmText">確認轉移</label>
      </FloatLabel>
    </div>

    <!-- 錯誤訊息 -->
    <Message v-if="error" severity="error" :closable="false">
      {{ error }}
    </Message>

    <!-- 操作按鈕 -->
    <template #footer>
      <Button label="取消" @click="visible = false" />
      <Button
        label="確認轉移"
        severity="danger"
        @click="confirmTransfer"
        :loading="loading"
        :disabled="!canTransfer"
      />
    </template>
  </Dialog>
</template>

<script setup>
const canTransfer = computed(() => {
  return selectedMemberId.value && confirmText.value === "轉移擁有權";
});

const confirmTransfer = async () => {
  if (!canTransfer.value) return;

  loading.value = true;
  error.value = null;

  try {
    const response = await $fetch(
      `${config.public.apiBase}/api/v1/channelmemberapi/channel/${channelId}/transfer-ownership/${selectedMemberId.value}`,
      {
        method: "POST",
        credentials: "include",
        headers: {
          Authorization: `Bearer ${userStore.accessToken}`,
          "Content-Type": "application/json",
        },
      }
    );

    if (response.success) {
      // 轉移成功，刷新頻道資料
      emit("transferred", response.data);
      visible.value = false;

      // 顯示成功訊息
      toast.add({
        severity: "success",
        summary: "轉移成功",
        detail: response.message,
        life: 3000,
      });
    }
  } catch (error) {
    error.value = error.data?.message || "轉移失敗";
  } finally {
    loading.value = false;
  }
};
</script>
```

### 2. 頻道設定界面 (含成員數量顯示)

#### 頻道設定對話框 (`ChannelSettingsDialog.vue`)

```vue
<template>
  <Dialog v-model:visible="visible" header="頻道設定">
    <!-- 基本設定 -->
    <div class="channel-basic-settings">
      <FloatLabel>
        <InputText id="channelName" v-model="channelName" />
        <label for="channelName">頻道名稱</label>
      </FloatLabel>

      <FloatLabel>
        <Textarea id="description" v-model="description" />
        <label for="description">頻道描述</label>
      </FloatLabel>
    </div>

    <!-- 加入方式設定 -->
    <div class="join-settings">
      <h4>加入方式</h4>

      <div class="setting-item">
        <Checkbox id="allowJoinById" v-model="allowJoinById" />
        <label for="allowJoinById">允許通過頻道ID加入</label>
      </div>

      <div class="setting-item">
        <Checkbox id="passwordRequired" v-model="passwordRequired" />
        <label for="passwordRequired">需要密碼才能加入</label>
      </div>

      <!-- 密碼設定 -->
      <div v-if="passwordRequired" class="password-setting">
        <FloatLabel>
          <Password
            id="joinPassword"
            v-model="joinPassword"
            placeholder="設定頻道密碼"
            :feedback="false"
            toggleMask
          />
          <label for="joinPassword">頻道密碼</label>
        </FloatLabel>
      </div>
    </div>

    <!-- 頻道資訊顯示 -->
    <div v-if="allowJoinById" class="channel-info">
      <h4>分享資訊</h4>
      <div class="share-info">
        <p><strong>頻道 ID:</strong> {{ channelId }}</p>
        <p><strong>成員數量:</strong> {{ memberCount }} 人</p>
        <Button label="複製ID" size="small" @click="copyChannelId" />
      </div>
    </div>

    <!-- 操作按鈕 -->
    <template #footer>
      <Button label="取消" @click="visible = false" />
      <Button label="儲存設定" @click="saveSettings" :loading="loading" />
    </template>
  </Dialog>
</template>
```

### 3. 用戶流程設計

#### 🆕 加入頻道流程 (通過 ID + 密碼)

1. **用戶操作**:

   - 點擊「加入頻道」按鈕 → 開啟加入對話框
   - 輸入頻道 ID → 輸入密碼 → 點擊加入
   - 驗證成功後自動進入頻道

2. **創建者分享流程**:
   - 頻道設定 → 啟用「允許通過 ID 加入」
   - 設定頻道密碼 → 複製頻道 ID
   - 分享頻道 ID 和密碼給目標用戶

#### 🔄 擁有權轉移流程

1. **Owner 要離開頻道**:

   - 點擊「離開頻道」→ 系統檢測到需要轉移擁有權
   - 顯示轉移對話框 → 選擇新的擁有者
   - 輸入確認文字 → 執行轉移

2. **轉移後的變化**:
   - 原 Owner → Admin 角色
   - 新 Owner → 獲得完整頻道控制權
   - 頻道 creator_id 更新

#### 成員管理流程

1. **查看成員**: 頻道側邊欄顯示所有成員，按角色排序
2. **角色管理**: 長按成員 → 顯示操作選單 → 更改角色/移除成員
3. **離開頻道**:
   - 一般成員：直接離開
   - Owner：需要先轉移擁有權才能離開

## 🔐 權限控制機制

### 1. 角色定義

| 角色               | 權限                                              |
| ------------------ | ------------------------------------------------- |
| **Owner (創建者)** | 所有權限，包括刪除頻道、轉讓擁有權                |
| **Admin (管理員)** | 邀請/移除成員、更改成員角色（除 Owner）、頻道設定 |
| **Member (成員)**  | 發送訊息、查看訊息歷史、離開頻道                  |

### 2. 權限檢查邏輯

#### 後端權限裝飾器

```python
def channel_permission_required(permission: str):
    """頻道權限檢查裝飾器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            channel_id = kwargs.get('channel_id')
            user_id = g.user.id

            # 檢查用戶在頻道中的角色和權限
            member = db.session.query(ChannelMember).filter_by(
                channel_id=channel_id,
                user_id=user_id,
                status='active'
            ).first()

            if not member or not has_channel_permission(member.role, permission):
                return jsonify({'error': '權限不足'}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def has_channel_permission(role: str, permission: str) -> bool:
    """檢查角色是否具有特定權限"""
    permissions = {
        'owner': ['all'],
        'admin': ['invite_members', 'remove_members', 'change_roles', 'edit_channel'],
        'member': ['send_messages', 'view_messages', 'leave_channel']
    }

    role_permissions = permissions.get(role, [])
    return permission in role_permissions or 'all' in role_permissions
```

#### 前端權限檢查

```typescript
// stores/channel.ts 新增方法
canInviteMembers(channelId: number): boolean {
  const member = this.getCurrentUserChannelRole(channelId)
  return member?.role in ['owner', 'admin']
}

canRemoveMember(channelId: number, targetUserId: number): boolean {
  const currentMember = this.getCurrentUserChannelRole(channelId)
  const targetMember = this.getChannelMember(channelId, targetUserId)

  // Owner 可以移除任何人，Admin 可以移除 Member
  if (currentMember?.role === 'owner') return true
  if (currentMember?.role === 'admin' && targetMember?.role === 'member') return true

  return false
}
```

## 📡 WebSocket 即時通知

### 1. Socket.IO 事件設計

#### 後端事件 (`socketio_server.py`)

```python
@socketio.on('join_private_channel')
def handle_join_private_channel(data):
    """加入私人頻道"""
    channel_id = data.get('channel_id')

    # 檢查用戶是否有權限加入
    if not can_access_channel(g.user.id, channel_id):
        emit('error', {'message': '無權限加入此頻道'})
        return

    join_room(f'channel_{channel_id}')
    emit('joined_channel', {'channel_id': channel_id})

@socketio.on('send_channel_invitation')
def handle_send_invitation(data):
    """發送頻道邀請通知"""
    invitee_ids = data.get('invitee_ids', [])
    channel_id = data.get('channel_id')

    for invitee_id in invitee_ids:
        # 發送即時邀請通知給被邀請者
        emit('channel_invitation', {
            'channel_id': channel_id,
            'channel_name': data.get('channel_name'),
            'inviter_name': g.user.username,
            'message': data.get('message', ''),
            'invitation_id': data.get('invitation_id')
        }, room=f'user_{invitee_id}')
```

#### 前端事件處理 (`useSocket.ts`)

```typescript
// 監聽頻道邀請
socket.value.on("channel_invitation", (data) => {
  console.log("收到頻道邀請:", data);

  // 顯示邀請通知
  showInvitationNotification({
    channelName: data.channel_name,
    inviterName: data.inviter_name,
    message: data.message,
    invitationId: data.invitation_id,
  });
});

// 監聽成員變更
socket.value.on("channel_member_updated", (data) => {
  console.log("頻道成員更新:", data);
  channelStore.updateChannelMember(data.channel_id, data.member);
});
```

## 📝 實作優先級

### Phase 1: 基礎功能 (高優先級)

1. ✅ 資料庫架構實作 (`ChannelMember` 模型)
2. ✅ 成員數量同步 Hook 系統 🔄
3. ✅ 基本 API 端點 (ID+密碼加入、離開、移除)
4. ✅ 權限控制機制
5. ✅ 前端基本 UI (加入對話框、成員列表)

### Phase 2: 進階功能 (中優先級)

1. 📋 即時通知 (WebSocket 事件)
2. 📋 成員角色管理
3. 📋 頻道密碼加密存儲 (bcrypt)
4. 📋 成員數量實時同步前端顯示

### Phase 3: 優化功能 (低優先級)

1. 📋 成員活動記錄
2. 📋 批量操作
3. 📋 成員統計分析
4. 📋 成員數量緩存優化

## 🧪 測試計畫

### 1. 單元測試

- 權限檢查邏輯
- API 端點功能
- 資料模型驗證
- 🔄 成員數量同步 Hook 測試
- 🛡️ 防重入機制測試
- 🔄 擁有權轉移邏輯測試

### 2. 整合測試

- ID+密碼加入流程完整性
- WebSocket 通知機制
- 前後端資料同步
- 🔄 成員數量實時更新測試
- 🛡️ 多次點擊防護測試
- 🔄 Owner 離開流程測試

### 3. 用戶測試

- ID+密碼加入用戶體驗
- 成員管理操作
- 權限控制效果
- 成員數量顯示準確性
- 🔄 擁有權轉移用戶體驗

## 🚀 部署注意事項

### 1. 資料庫遷移

```python
# 新增遷移腳本
from alembic import op
import sqlalchemy as sa

def upgrade():
    # 創建 channel_members 表
    op.create_table('channel_members', ...)

    # 創建 channel_invitations 表
    op.create_table('channel_invitations', ...)

    # 為現有頻道創建 owner 記錄，並同步更新成員數量
    op.execute("""
        INSERT INTO channel_members (channel_id, user_id, role, status, joined_at)
        SELECT id, creator_id, 'owner', 'active', created_on
        FROM chat_channels
    """)

    # 🔄 初始化所有頻道的成員數量
    op.execute("""
        UPDATE chat_channels
        SET member_count = (
            SELECT COUNT(*) FROM channel_members
            WHERE channel_members.channel_id = chat_channels.id
            AND channel_members.status = 'active'
        )
    """)
```

### 2. 配置更新

```python
# config.py 新增配置
MAX_CHANNEL_MEMBERS = 1000              # 最大成員數
CHANNEL_PASSWORD_MIN_LENGTH = 6        # 頻道密碼最小長度
ENABLE_MEMBER_COUNT_SYNC = True        # 啟用成員數量同步 Hook
BCRYPT_LOG_ROUNDS = 12                 # bcrypt 加密強度

# 新增依賴
# requirements.txt 或 pyproject.toml
flask-bcrypt>=1.0.1
```

---

**文檔版本**: v1.0  
**最後更新**: 2024-08-18  
**作者**: Claude Code Assistant  
**狀態**: 規劃階段
