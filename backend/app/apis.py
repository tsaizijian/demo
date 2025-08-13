from flask_appbuilder.api import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask import request, jsonify, g
from flask_appbuilder.security.decorators import has_access
from flask_appbuilder import expose
import datetime

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

    def pre_add(self, obj):
        """在添加前自動設定sender_id"""
        obj.sender_id = g.user.id
        obj.channel_id = getattr(obj, 'channel_id', 1)  # 預設頻道

    def pre_update(self, obj):
        """防止修改sender_id"""
        pass

    @expose('/recent/<int:limit>')
    @has_access
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
    @has_access
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
                created_on=datetime.datetime.utcnow(),
                changed_on=datetime.datetime.utcnow()
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
    @has_access
    def message_history(self):
        """
        取得歷史訊息 (分頁)
        GET /api/v1/chatmessageapi/history?page=1&per_page=20&before_id=100
        """
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        before_id = request.args.get('before_id', type=int)  # 取得指定 ID 之前的訊息
        channel_id = request.args.get('channel_id', 1, type=int)

        query = (
            self.datamodel.session.query(ChatMessage)
            .filter(ChatMessage.is_deleted == False)
            .filter(ChatMessage.channel_id == channel_id)
        )

        # 如果指定 before_id，取得該 ID 之前的訊息
        if before_id:
            query = query.filter(ChatMessage.id < before_id)

        # 分頁查詢
        pagination = query.order_by(ChatMessage.created_on.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        messages = list(reversed(pagination.items))  # 反轉讓最舊的在前面

        return jsonify({
            'result': [msg.to_dict() for msg in messages],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })

    @expose('/delete/<int:message_id>', methods=['POST'])
    @has_access
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

    def pre_add(self, obj):
        """在添加前自動設定user_id"""
        obj.user_id = g.user.id
        obj.join_date = datetime.datetime.utcnow()

    @expose('/me')
    @has_access
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
                join_date=datetime.datetime.utcnow()
            )
            self.datamodel.add(profile)

        return jsonify({
            'result': profile.to_dict()
        })

    @expose('/update-profile', methods=['POST'])
    @has_access
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
    @has_access
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
    @has_access
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
            profile.last_seen = datetime.datetime.utcnow()
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
    
    # 設定基本權限，允許已認證使用者存取
    base_permissions = [
        'can_get',
        'can_put', 
        'can_post',
        'can_delete',
        'can_get_public_channels',
        'can_create_channel',
        'can_get_my_channels'
    ]

    # 簡化欄位配置
    list_columns = ['id', 'name', 'description', 'is_active', 'created_on']
    show_columns = ['id', 'name', 'description', 'is_active', 'created_on']
    add_columns = ['name', 'description']
    edit_columns = ['name', 'description', 'is_active']

    # 預設排序
    base_order = ('created_on', 'desc')

    def pre_add(self, obj):
        """在添加前自動設定creator_id"""
        obj.creator_id = g.user.id

    @expose('/public-channels')
    @has_access
    def get_public_channels(self):
        """
        取得公開頻道列表
        GET /api/v1/chatchannel/public-channels
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

        return jsonify({
            'result': [channel.to_dict() for channel in channels],
            'count': len(channels)
        })

    @expose('/create-channel', methods=['POST'])
    @has_access
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
                max_members=data.get('max_members', 100)
            )

            # 使用直接的資料庫操作
            self.datamodel.session.add(channel)
            self.datamodel.session.commit()
            
            # 重新整理以取得資料庫分配的ID
            self.datamodel.session.refresh(channel)

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
    @has_access
    def get_my_channels(self):
        """
        取得我建立的頻道
        GET /api/v1/chatchannel/my-channels
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
            .order_by(ChatChannel.created_on.desc())
            .all()
        )

        return jsonify({
            'result': [channel.to_dict() for channel in channels],
            'count': len(channels)
        })