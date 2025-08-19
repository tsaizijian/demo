from flask_appbuilder.api import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask import request, jsonify, g
# from flask_appbuilder.security.decorators import has_access
from .auth import jwt_required
from flask_appbuilder import expose
import datetime
from datetime import timezone
from .time_utils import to_iso_utc


from .models import ChatMessage, UserProfile, ChatChannel


class ChatMessageApi(ModelRestApi):
    """
    聊天室訊息 REST API
    提供 CRUD 操作與自訂查詢功能
    """
    datamodel = SQLAInterface(ChatMessage)

    # 允許的操作方法
    allow_browser_login = True

    # 簡化欄位配置，避免schema問題
    # API 回傳欄位控制 - 只使用基本欄位
    list_columns = ['id', 'content', 'message_type', 'created_on']
    show_columns = ['id', 'content', 'message_type', 'created_on', 'changed_on']
    add_columns = ['content', 'message_type']
    edit_columns = ['content']

    # 搜尋功能
    search_columns = ['content']

    # 預設排序 (最新訊息在前)
    base_order = ('created_on', 'desc')

    # 單頁最大筆數限制
    max_page_size = 100
    
    # 🔒 安全性：禁用危險的 REST 端點
    base_permissions = []

    def pre_add(self, obj):
        """在添加前自動設定sender_id"""
        obj.sender_id = g.user.id
        obj.channel_id = getattr(obj, 'channel_id', 1)  # 預設頻道

    def pre_update(self, obj):
        """🔒 安全檢查：用戶只能修改自己的訊息"""
        if not g.user:
            raise Exception("未認證")
        if obj.sender_id != g.user.id and not self._is_admin():
            raise Exception("無權限修改其他用戶的訊息")
    
    def pre_delete(self, obj):
        """🔒 安全檢查：用戶只能刪除自己的訊息"""
        if not g.user:
            raise Exception("未認證")
        if obj.sender_id != g.user.id and not self._is_admin():
            raise Exception("無權限刪除其他用戶的訊息")
    
    def pre_get(self, obj):
        """🔒 安全檢查：檢查用戶是否有權限查看該訊息的頻道"""
        if not g.user:
            raise Exception("未認證")
        # 檢查用戶是否有權限存取該頻道的訊息
        if not self._can_access_channel(obj.channel_id):
            raise Exception("無權限查看此頻道的訊息")
    
    def _can_access_channel(self, channel_id):
        """檢查用戶是否有權限存取指定頻道"""
        from .models import ChatChannel
        channel = self.datamodel.session.query(ChatChannel).filter(ChatChannel.id == channel_id).first()
        if not channel:
            return False
        # 公開頻道所有人都可以存取，私人頻道需要是創建者
        if not channel.is_private:
            return True
        return channel.creator_id == g.user.id or self._is_admin()
    
    def _is_admin(self):
        """檢查當前用戶是否為管理員"""
        return hasattr(g.user, 'roles') and any(role.name == 'Admin' for role in g.user.roles)

    @expose('/recent/<int:limit>')
    @jwt_required
    def recent_messages(self, limit=50):
        """
        取得最近的訊息
        GET /api/v1/chatmessage/recent/50?channel_id=1
        """
        if limit > 100:
            limit = 100

        # 從查詢參數獲取 channel_id，預設為 1
        channel_id = request.args.get('channel_id', 1, type=int)

        messages = (
            self.datamodel.session.query(ChatMessage)
            .filter(ChatMessage.is_deleted == False)
            .filter(ChatMessage.channel_id == channel_id)
            .order_by(ChatMessage.created_on.desc())
            .limit(limit)
            .all()
        )

        # 反轉順序讓最舊的在前面
        messages = list(reversed(messages))

        return jsonify({
            'result': [msg.to_dict() for msg in messages],
            'count': len(messages)
        })

    @expose('/send', methods=['POST'])
    @jwt_required
    def send_message(self):
        """
        發送新訊息
        POST /api/v1/chatmessageapi/send
        """
        try:
            data = request.get_json()

            # 驗證必要欄位
            if not data or 'content' not in data:
                return jsonify({'error': '訊息內容不能為空'}), 400
            
            # 驗證 channel_id 是必需的
            channel_id = data.get('channel_id')
            if not channel_id:
                return jsonify({'error': '必須指定頻道ID'}), 400

            # 建立新訊息
            message = ChatMessage(
                content=data['content'],
                sender_id=g.user.id,  # 當前登入使用者
                message_type=data.get('message_type', 'text'),
                attachment_path=data.get('attachment_path'),
                reply_to_id=data.get('reply_to_id'),
                channel_id=channel_id,
                # 手動設定 AuditMixin 欄位
                created_by_fk=g.user.id,
                changed_by_fk=g.user.id,
                created_on = datetime.now(),
                changed_on = datetime.now()
            )

            # 儲存到資料庫
            self.datamodel.add(message)

            # 回傳新建立的訊息資料
            return jsonify({
                'message': '訊息發送成功',
                'data': message.to_dict()
            }), 201

        except Exception as e:
            return jsonify({'error': f'發送失敗: {str(e)}'}), 500

    @expose('/history')
    @jwt_required
    def message_history(self):
        """
        取得歷史訊息（游標式分頁）
        GET /api/v1/chatmessageapi/history?channel_id=1&per_page=20&before_id=100
        - 不帶 before_id：抓最新一頁
        - 帶 before_id：抓該 id 之前的舊訊息
        """
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        before_id = request.args.get('before_id', type=int)
        channel_id = request.args.get('channel_id', 1, type=int)

        q = (
            self.datamodel.session.query(ChatMessage)
            .filter(ChatMessage.is_deleted.is_(False))
            .filter(ChatMessage.channel_id == channel_id)
        )

        if before_id:
            q = q.filter(ChatMessage.id < before_id)

        rows = (
            q.order_by(ChatMessage.id.desc())
             .limit(per_page + 1)
             .all()
        )

        has_next = len(rows) > per_page
        if has_next:
            rows = rows[:per_page]

        rows = list(reversed(rows))
        next_before_id = rows[0].id if has_next and rows else None

        return jsonify({
            'result': [r.to_dict() for r in rows],
            'pagination': {
                'per_page': per_page,
                'has_next': has_next,
                'next_before_id': next_before_id
            }
        })

    @expose('/delete/<int:message_id>', methods=['POST'])
    @jwt_required
    def soft_delete_message(self, message_id):
        """
        軟刪除訊息 (只有發送者或管理員可刪除)
        POST /api/v1/chatmessageapi/delete/123
        """
        message = self.datamodel.get(message_id)

        if not message:
            return jsonify({'error': '訊息不存在'}), 404

        # 權限檢查：只有發送者或管理員可以刪除
        if message.sender_id != g.user.id and not g.user.is_admin():
            return jsonify({'error': '沒有權限刪除此訊息'}), 403

        # 軟刪除
        message.is_deleted = True
        self.datamodel.edit(message)

        return jsonify({'message': '訊息已刪除'})


class UserProfileApi(ModelRestApi):
    """
    使用者資料擴充 REST API
    """
    datamodel = SQLAInterface(UserProfile)

    allow_browser_login = True

    # 簡化欄位配置
    list_columns = ['id', 'display_name', 'is_online', 'join_date']
    show_columns = ['id', 'display_name', 'bio', 'is_online', 'join_date']
    add_columns = ['display_name', 'bio']
    edit_columns = ['display_name', 'bio']

    # 預設排序
    base_order = ('join_date', 'desc')
    
    # 🔒 安全性：禁用不安全的端點
    # 禁用列出所有用戶的端點
    list_template = None
    # 禁用 REST API 的危險端點
    base_permissions = []

    def pre_add(self, obj):
        """在添加前自動設定user_id"""
        obj.user_id = g.user.id
        obj.join_date = datetime.datetime.now(timezone.utc)
    
    def pre_get(self, obj):
        """🔒 安全檢查：用戶只能查看自己的 profile"""
        if not g.user:
            raise Exception("未認證")
        if obj.user_id != g.user.id and not self._is_admin():
            raise Exception("無權限查看其他用戶的個人資料")
    
    def pre_update(self, obj):
        """🔒 安全檢查：用戶只能修改自己的 profile"""  
        if not g.user:
            raise Exception("未認證")
        if obj.user_id != g.user.id and not self._is_admin():
            raise Exception("無權限修改其他用戶的個人資料")
    
    def pre_delete(self, obj):
        """🔒 安全檢查：用戶只能刪除自己的 profile"""
        if not g.user:
            raise Exception("未認證")
        if obj.user_id != g.user.id and not self._is_admin():
            raise Exception("無權限刪除其他用戶的個人資料")
    
    def _is_admin(self):
        """檢查當前用戶是否為管理員"""
        return hasattr(g.user, 'roles') and any(role.name == 'Admin' for role in g.user.roles)

    @expose('/me')
    @jwt_required
    def get_my_profile(self):
        """
        取得當前使用者的個人資料
        GET /api/v1/userprofileapi/me
        """
        profile = (
            self.datamodel.session.query(UserProfile)
            .filter(UserProfile.user_id == g.user.id)
            .first()
        )

        if not profile:
            # 如果沒有個人資料，建立一個
            profile = UserProfile(
                user_id=g.user.id,
                display_name=g.user.username,
                join_date=datetime.datetime.now(timezone.utc)
            )
            self.datamodel.add(profile)

        return jsonify({
            'result': profile.to_dict()
        })

    @expose('/update-profile', methods=['POST'])
    @jwt_required
    def update_my_profile(self):
        """
        更新當前使用者的個人資料
        POST /api/v1/userprofileapi/update-profile
        """
        try:
            data = request.get_json()

            profile = (
                self.datamodel.session.query(UserProfile)
                .filter(UserProfile.user_id == g.user.id)
                .first()
            )

            if not profile:
                profile = UserProfile(user_id=g.user.id)
                self.datamodel.add(profile)

            # 更新允許的欄位
            allowed_fields = ['display_name', 'avatar_url', 'bio', 'timezone', 'language', 'notification_settings']
            for field in allowed_fields:
                if field in data:
                    setattr(profile, field, data[field])

            self.datamodel.edit(profile)

            return jsonify({
                'message': '個人資料更新成功',
                'data': profile.to_dict()
            })

        except Exception as e:
            return jsonify({'error': f'更新失敗: {str(e)}'}), 500

    @expose('/online-users')
    @jwt_required
    def get_online_users(self):
        """
        取得線上使用者列表
        GET /api/v1/userprofileapi/online-users
        """
        online_profiles = (
            self.datamodel.session.query(UserProfile)
            .filter(UserProfile.is_online == True)
            .order_by(UserProfile.last_seen.desc())
            .all()
        )

        return jsonify({
            'result': [profile.to_dict() for profile in online_profiles],
            'count': len(online_profiles)
        })

    @expose('/set-online-status', methods=['POST'])
    @jwt_required
    def set_online_status(self):
        """
        設定線上狀態
        POST /api/v1/userprofileapi/set-online-status
        """
        try:
            data = request.get_json()
            is_online = data.get('is_online', True)

            profile = (
                self.datamodel.session.query(UserProfile)
                .filter(UserProfile.user_id == g.user.id)
                .first()
            )

            if not profile:
                profile = UserProfile(user_id=g.user.id)
                self.datamodel.add(profile)

            profile.is_online = is_online
            profile.last_seen = datetime.datetime.now(timezone.utc)
            self.datamodel.edit(profile)

            return jsonify({
                'message': f'線上狀態已設定為: {"上線" if is_online else "離線"}',
                'data': {'is_online': is_online, 'last_seen': profile.last_seen.isoformat()}
            })

        except Exception as e:
            return jsonify({'error': f'設定失敗: {str(e)}'}), 500


class ChatChannelApi(ModelRestApi):
    """
    聊天頻道 REST API
    """
    datamodel = SQLAInterface(ChatChannel)

    allow_browser_login = True
    
    # 🔒 安全性：禁用危險的 REST 端點，只保留自定義端點
    base_permissions = [
        'can_get_public_channels',
        'can_create_channel',
        'can_get_my_channels',
        'can_put'  # 允許 PUT 請求編輯權限
    ]

    # 簡化欄位配置
    list_columns = ['id', 'name', 'description', 'is_active', 'created_on']
    show_columns = ['id', 'name', 'description', 'is_active', 'created_on']
    add_columns = ['name', 'description']
    edit_columns = ['name', 'description', 'is_active', 'is_private', 'max_members', 'allow_join_by_id', 'password_required']

    # 預設排序
    base_order = ('created_on', 'desc')

    def pre_add(self, obj):
        """在添加前自動設定creator_id"""
        obj.creator_id = g.user.id
    
    def pre_get(self, obj):
        """🔒 安全檢查：用戶只能查看有權限的頻道"""
        if not g.user:
            raise Exception("未認證")
        # 公開頻道所有人都可以查看，私人頻道只有創建者可以查看
        if obj.is_private and obj.creator_id != g.user.id and not self._is_admin():
            raise Exception("無權限查看此私人頻道")
    
    def pre_update(self, obj):
        """🔒 安全檢查：只有頻道創建者、管理員或系統管理員可以修改頻道"""
        if not g.user:
            raise Exception("未認證")
        
        # 系統管理員可以修改任何頻道
        if self._is_admin():
            return
            
        # 檢查是否為頻道創建者
        if obj.creator_id == g.user.id:
            return
            
        # 檢查是否為頻道管理員 (owner/admin)
        from .models import ChannelMember
        member = self.datamodel.session.query(ChannelMember).filter_by(
            channel_id=obj.id,
            user_id=g.user.id,
            status='active'
        ).first()
        
        if member and member.role in ['owner', 'admin']:
            return
            
        raise Exception("無權限修改此頻道")
    
    def pre_delete(self, obj):
        """🔒 安全檢查：用戶只能刪除自己創建的頻道"""
        if not g.user:
            raise Exception("未認證")
        if obj.creator_id != g.user.id and not self._is_admin():
            raise Exception("無權限刪除此頻道")
    
    def _is_admin(self):
        """檢查當前用戶是否為管理員"""
        return hasattr(g.user, 'roles') and any(role.name == 'Admin' for role in g.user.roles)

    @expose('/public-channels')
    @jwt_required
    def get_public_channels(self):
        """
        取得公開頻道列表 (包含最新訊息)
        GET /api/v1/chatchannelapi/public-channels
        """
        # 簡單的認證檢查
        if not hasattr(g, 'user') or not g.user:
            return jsonify({'error': '未登入'}), 401
            
        channels = (
            self.datamodel.session.query(ChatChannel)
            .filter(ChatChannel.is_private == False)
            .filter(ChatChannel.is_active == True)
            .order_by(ChatChannel.created_on.desc())
            .all()
        )

        # 為每個頻道添加最新訊息資訊
        result = []
        for channel in channels:
            channel_data = channel.to_dict()
            
            # 查詢該頻道的最新訊息
            latest_message = (
                self.datamodel.session.query(ChatMessage)
                .filter(ChatMessage.channel_id == channel.id)
                .filter(ChatMessage.is_deleted == False)
                .order_by(ChatMessage.created_on.desc())
                .first()
            )
            
            if latest_message:
                channel_data['lastMessage'] = {
                    'id': latest_message.id,
                    'content': latest_message.content,
                    'sender_name': latest_message.sender.username if latest_message.sender else 'Unknown',
                    'created_on': to_iso_utc(latest_message.created_on)
                }
            else:
                channel_data['lastMessage'] = None
                
            result.append(channel_data)

        return jsonify({
            'result': result,
            'count': len(result)
        })

    @expose('/create-channel', methods=['POST'])
    @jwt_required
    def create_channel(self):
        """
        建立新頻道
        POST /api/v1/chatchannel/create-channel
        """
        try:
            # 詳細的認證檢查
            if not hasattr(g, 'user') or not g.user:
                print("認證失敗: g.user 不存在")
                return jsonify({'error': '未登入或認證失敗'}), 401
            
            # 檢查是否為匿名使用者
            if g.user.__class__.__name__ == 'AnonymousUserMixin':
                print("認證失敗: 使用者為 AnonymousUserMixin")
                return jsonify({'error': '未認證使用者'}), 401
            
            # 檢查使用者是否有 id 屬性
            if not hasattr(g.user, 'id'):
                print(f"認證失敗: 使用者物件沒有 id 屬性, 類型: {type(g.user)}")
                return jsonify({'error': '使用者物件無效'}), 401
                
            print(f"認證成功: user_id={g.user.id}, username={getattr(g.user, 'username', 'N/A')}")
            data = request.get_json()

            # 驗證必要欄位
            if not data or 'name' not in data:
                return jsonify({'error': '頻道名稱不能為空'}), 400

            # 建立新頻道
            channel = ChatChannel(
                name=data['name'],
                description=data.get('description', ''),
                is_private=data.get('is_private', False),
                creator_id=g.user.id,
                max_members=data.get('max_members', 100),
                allow_join_by_id=data.get('allow_join_by_id', False),
                password_required=data.get('password_required', False)
            )

            # 處理密碼設定
            if data.get('password_required') and data.get('join_password'):
                from flask_bcrypt import Bcrypt
                bcrypt = Bcrypt()
                channel.join_password = bcrypt.generate_password_hash(data.get('join_password')).decode('utf-8')

            # 使用直接的資料庫操作
            self.datamodel.session.add(channel)
            self.datamodel.session.commit()
            
            # 重新整理以取得資料庫分配的ID
            self.datamodel.session.refresh(channel)
            
            # 🔧 修復：自動將創建者加入為該頻道的擁有者成員
            from .models import ChannelMember
            creator_member = ChannelMember(
                channel_id=channel.id,
                user_id=g.user.id,
                role='owner',
                status='active',
                created_by_fk=g.user.id,
                changed_by_fk=g.user.id
            )
            self.datamodel.session.add(creator_member)
            self.datamodel.session.commit()

            return jsonify({
                'message': '頻道建立成功',
                'data': channel.to_dict()
            }), 201

        except Exception as e:
            # 回滾資料庫變更
            self.datamodel.session.rollback()
            # 印出詳細錯誤供調試
            import traceback
            print(f"建立頻道時發生錯誤: {str(e)}")
            print(f"錯誤堆疊: {traceback.format_exc()}")
            return jsonify({'error': f'建立失敗: {str(e)}'}), 500

    @expose('/my-channels')
    @jwt_required
    def get_my_channels(self):
        """
        取得我建立的頻道 (包含最新訊息)
        GET /api/v1/chatchannelapi/my-channels
        """
        # 詳細的認證檢查
        if not hasattr(g, 'user') or not g.user:
            return jsonify({'error': '未登入'}), 401
        
        # 檢查是否為匿名使用者
        if g.user.__class__.__name__ == 'AnonymousUserMixin':
            print("認證失敗: 使用者為 AnonymousUserMixin")
            return jsonify({'error': '未認證使用者'}), 401
        
        # 檢查使用者是否有 id 屬性
        if not hasattr(g.user, 'id'):
            print(f"認證失敗: 使用者物件沒有 id 屬性, 類型: {type(g.user)}")
            return jsonify({'error': '使用者物件無效'}), 401
            
        print(f"取得我的頻道 - 認證成功: user_id={g.user.id}, username={getattr(g.user, 'username', 'N/A')}")
            
        channels = (
            self.datamodel.session.query(ChatChannel)
            .filter(ChatChannel.creator_id == g.user.id)
            .filter(ChatChannel.is_active == True)
            .order_by(ChatChannel.created_on.desc())
            .all()
        )

        # 為每個頻道添加最新訊息資訊
        result = []
        for channel in channels:
            channel_data = channel.to_dict()
            
            # 查詢該頻道的最新訊息
            latest_message = (
                self.datamodel.session.query(ChatMessage)
                .filter(ChatMessage.channel_id == channel.id)
                .filter(ChatMessage.is_deleted == False)
                .order_by(ChatMessage.created_on.desc())
                .first()
            )
            
            if latest_message:
                channel_data['lastMessage'] = {
                    'id': latest_message.id,
                    'content': latest_message.content,
                    'sender_name': latest_message.sender.username if latest_message.sender else 'Unknown',
                    'created_on': to_iso_utc(latest_message.created_on)
                }
            else:
                channel_data['lastMessage'] = None
                
            result.append(channel_data)

        return jsonify({
            'result': result,
            'count': len(result)
        })
    @expose("/delete-channel/<int:channel_id>", methods=["POST"])
    @jwt_required
    def delete_channel(self, channel_id):
        """
        軟刪除聊天室 (設定 is_active = False)
        POST /api/v1/chatchannelapi/delete-channel/123
        """
        try:
            # 詳細的認證檢查
            if not hasattr(g, "user") or not g.user:
                return jsonify({"error": "未登入或認證失敗"}), 401
            
            # 檢查是否為匿名使用者
            if g.user.__class__.__name__ == "AnonymousUserMixin":
                return jsonify({"error": "未認證使用者"}), 401
            
            # 檢查使用者是否有 id 屬性
            if not hasattr(g.user, "id"):
                return jsonify({"error": "使用者物件無效"}), 401
                
            print(f"刪除頻道請求 - 認證成功: user_id={g.user.id}, username={getattr(g.user, 'username', 'N/A')}")
            
            # 查詢頻道
            channel = self.datamodel.get(channel_id)
            if not channel:
                return jsonify({"error": "頻道不存在"}), 404
            
            # 檢查頻道是否已經被刪除
            if not channel.is_active:
                return jsonify({"error": "頻道已被刪除"}), 400
            
            # 權限檢查：只有創建者或管理員可以刪除
            is_admin = hasattr(g.user, "roles") and any(role.name == "Admin" for role in g.user.roles)
            is_creator = channel.creator_id == g.user.id
            
            if not (is_creator or is_admin):
                return jsonify({"error": "沒有權限刪除此頻道"}), 403
            
            # 防止刪除預設頻道 (ID = 1)
            if channel.id == 1:
                return jsonify({"error": "無法刪除預設頻道"}), 400
            
            # 軟刪除：設定 is_active = False
            channel.is_active = False
            channel.changed_by_fk = g.user.id
            channel.changed_on = datetime.datetime.now(timezone.utc)
            
            # 儲存變更
            self.datamodel.edit(channel)
            
            print(f"頻道 {channel.name} (ID: {channel.id}) 已被用戶 {g.user.username} 軟刪除")
            
            return jsonify({
                "message": f"頻道 \"{channel.name}\" 已成功刪除",
                "data": {
                    "channel_id": channel.id,
                    "channel_name": channel.name,
                    "deleted_by": g.user.username,
                    "deleted_at": channel.changed_on.isoformat()
                }
            }), 200

        except Exception as e:
            # 回滾資料庫變更
            self.datamodel.session.rollback()
            # 印出詳細錯誤供調試
            import traceback
            print(f"刪除頻道時發生錯誤: {str(e)}")
            print(f"錯誤堆疊: {traceback.format_exc()}")
            return jsonify({"error": f"刪除失敗: {str(e)}"}), 500

    @expose("/restore-channel/<int:channel_id>", methods=["POST"])
    @jwt_required
    def restore_channel(self, channel_id):
        """
        恢復已刪除的聊天室 (設定 is_active = True)
        POST /api/v1/chatchannelapi/restore-channel/123
        """
        try:
            # 詳細的認證檢查
            if not hasattr(g, "user") or not g.user:
                return jsonify({"error": "未登入或認證失敗"}), 401
            
            # 檢查是否為匿名使用者
            if g.user.__class__.__name__ == "AnonymousUserMixin":
                return jsonify({"error": "未認證使用者"}), 401
            
            # 檢查使用者是否有 id 屬性
            if not hasattr(g.user, "id"):
                return jsonify({"error": "使用者物件無效"}), 401
                
            print(f"恢復頻道請求 - 認證成功: user_id={g.user.id}, username={getattr(g.user, 'username', 'N/A')}")
            
            # 查詢頻道 (包含已刪除的)
            channel = self.datamodel.session.query(ChatChannel).filter(ChatChannel.id == channel_id).first()
            if not channel:
                return jsonify({"error": "頻道不存在"}), 404
            
            # 檢查頻道是否已經是啟用狀態
            if channel.is_active:
                return jsonify({"error": "頻道並未被刪除"}), 400
            
            # 權限檢查：只有創建者或管理員可以恢復
            is_admin = hasattr(g.user, "roles") and any(role.name == "Admin" for role in g.user.roles)
            is_creator = channel.creator_id == g.user.id
            
            if not (is_creator or is_admin):
                return jsonify({"error": "沒有權限恢復此頻道"}), 403
            
            # 恢復：設定 is_active = True
            channel.is_active = True
            channel.changed_by_fk = g.user.id
            channel.changed_on = datetime.datetime.now(timezone.utc)
            
            # 儲存變更
            self.datamodel.edit(channel)
            
            print(f"頻道 {channel.name} (ID: {channel.id}) 已被用戶 {g.user.username} 恢復")
            
            return jsonify({
                "message": f"頻道 \"{channel.name}\" 已成功恢復",
                "data": {
                    "channel_id": channel.id,
                    "channel_name": channel.name,
                    "restored_by": g.user.username,
                    "restored_at": channel.changed_on.isoformat()
                }
            }), 200

        except Exception as e:
            # 回滾資料庫變更
            self.datamodel.session.rollback()
            # 印出詳細錯誤供調試
            import traceback
            print(f"恢復頻道時發生錯誤: {str(e)}")
            print(f"錯誤堆疊: {traceback.format_exc()}")
            return jsonify({"error": f"恢復失敗: {str(e)}"}), 500

    @expose("/deleted-channels")
    @jwt_required
    def get_deleted_channels(self):
        """
        取得已刪除的頻道列表 (只有管理員或創建者可以存取)
        GET /api/v1/chatchannelapi/deleted-channels
        """
        try:
            # 詳細的認證檢查
            if not hasattr(g, "user") or not g.user:
                return jsonify({"error": "未登入或認證失敗"}), 401
            
            # 檢查是否為匿名使用者
            if g.user.__class__.__name__ == "AnonymousUserMixin":
                return jsonify({"error": "未認證使用者"}), 401
            
            # 檢查使用者是否有 id 屬性
            if not hasattr(g.user, "id"):
                return jsonify({"error": "使用者物件無效"}), 401
                
            print(f"查詢已刪除頻道 - 認證成功: user_id={g.user.id}, username={getattr(g.user, 'username', 'N/A')}")
            
            # 權限檢查：只有管理員或創建者可以查看已刪除的頻道
            is_admin = hasattr(g.user, "roles") and any(role.name == "Admin" for role in g.user.roles)
            
            if is_admin:
                # 管理員可以查看所有已刪除的頻道
                deleted_channels = (
                    self.datamodel.session.query(ChatChannel)
                    .filter(ChatChannel.is_active == False)
                    .order_by(ChatChannel.changed_on.desc())
                    .all()
                )
            else:
                # 一般用戶只能查看自己創建的已刪除頻道
                deleted_channels = (
                    self.datamodel.session.query(ChatChannel)
                    .filter(ChatChannel.is_active == False)
                    .filter(ChatChannel.creator_id == g.user.id)
                    .order_by(ChatChannel.changed_on.desc())
                    .all()
                )
            
            # 轉換為字典格式
            result = []
            for channel in deleted_channels:
                channel_data = channel.to_dict()
                channel_data["status"] = "deleted"
                channel_data["deleted_at"] = channel_data.get("changed_on")
                result.append(channel_data)
            
            return jsonify({
                "result": result,
                "count": len(result)
            })

        except Exception as e:
            # 印出詳細錯誤供調試
            import traceback
            print(f"查詢已刪除頻道時發生錯誤: {str(e)}")
            print(f"錯誤堆疊: {traceback.format_exc()}")
            return jsonify({"error": f"查詢失敗: {str(e)}"}), 500

