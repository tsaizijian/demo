from flask import request, g
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user
from flask_jwt_extended import decode_token, get_jwt_identity
from datetime import datetime, timezone
import jwt

from . import app, db, appbuilder
from .models import ChatMessage, UserProfile
from .time_utils import to_iso_utc, serialize_datetime_fields

socketio = SocketIO(app, 
                   cors_allowed_origins=["http://localhost:3000"],
                   logger=True, 
                   engineio_logger=True,
                   async_mode='threading',
                   ping_timeout=60,
                   ping_interval=25)

# 儲存線上使用者
online_users = {}

# 應用啟動時清理所有線上狀態
def reset_all_online_status():
    """重置所有使用者的線上狀態為離線"""
    try:
        with app.app_context():
            # 將所有使用者設為離線
            profiles = db.session.query(UserProfile).filter_by(is_online=True).all()
            for profile in profiles:
                profile.is_online = False
                profile.changed_on = datetime.now(timezone.utc)
                # 使用該使用者的 user_id 作為 changed_by_fk
                profile.changed_by_fk = profile.user_id
            
            db.session.commit()
            print(f"已重置 {len(profiles)} 個使用者的線上狀態為離線")
    except Exception as e:
        print(f"重置線上狀態失敗: {e}")
        import traceback
        traceback.print_exc()

# 延遲執行重置，避免在模組載入時影響 Socket.IO 初始化
def init_socketio():
    """初始化 Socket.IO 時重置線上狀態"""
    reset_all_online_status()

# 在這裡不執行重置，改為在應用啟動時執行

# 驗證JWT Token
def authenticate_socket(auth):
    """驗證Socket連接的JWT token"""
    if not auth or 'token' not in auth:
        return None
        
    token = auth['token']
    if not token:
        return None
        
    try:
        # 使用Flask-AppBuilder的JWT解碼
        import jwt
        
        # 獲取JWT設定
        secret_key = app.config.get('SECRET_KEY')
        algorithm = 'HS256'
        
        # 解碼JWT token
        decoded = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id = decoded.get('user_id') or decoded.get('sub')
        
        if not user_id:
            print("Token中沒有找到user_id")
            return None
        
        # 從資料庫獲取使用者 - 使用appbuilder的User模型
        User = appbuilder.sm.user_model
        user = db.session.query(User).filter_by(id=user_id).first()
        
        if user:
            print(f"Token驗證成功: {user.username}")
        else:
            print(f"找不到用戶ID: {user_id}")
            
        return user
    except jwt.ExpiredSignatureError:
        print("Token已過期")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Token無效: {e}")
        return None
    except Exception as e:
        print(f"Token驗證失敗: {e}")
        return None

@socketio.on('connect')
def on_connect(auth):
    """使用者連接"""
    print(f"Socket連接嘗試，auth: {auth}")
    
    # 嘗試使用Socket認證
    user = authenticate_socket(auth)
    
    # 如果Socket認證失敗，嘗試使用current_user（適用於同域Cookie）
    if not user and current_user and current_user.is_authenticated:
        user = current_user
    
    if not user:
        print(f"未認證使用者嘗試連接: {request.sid}")
        return False
    
    user_id = user.id
    username = user.username
    
    # 使用username作為主要顯示名稱，這樣更一致
    display_name = username
    first_name = getattr(user, 'first_name', '') or ''
    last_name = getattr(user, 'last_name', '') or ''
        
    print(f"使用者資訊: username={username}, first_name={first_name}, last_name={last_name}, display_name={display_name}")
    
    # 檢查該使用者是否已經在線，如果是，先移除舊連接
    existing_sids = []
    for sid, user_info in list(online_users.items()):
        if user_info['user_id'] == user_id:
            existing_sids.append(sid)
    
    # 移除該使用者的所有舊連接記錄
    for old_sid in existing_sids:
        if old_sid in online_users:
            print(f"移除使用者 {username} 的舊連接: {old_sid}")
            del online_users[old_sid]
    
    # 確保在記憶體中該使用者只有一個連接
    print(f"使用者 {username} 連接前: {len([u for u in online_users.values() if u['user_id'] == user_id])} 個連接")
    
    # 記錄新的線上使用者
    online_users[request.sid] = {
        'user_id': user_id,
        'username': username,
        'display_name': display_name,
        'connected_at': datetime.now().isoformat()
    }
    
    # 更新資料庫中的線上狀態
    try:
        # 設定 Flask g.user，這樣 AuditMixin 才能正確取得 user_id
        g.user = user
        print(f"🔍 DEBUG: 連線時已設定 g.user = {g.user.username} (ID: {g.user.id})")
        
        # 查找或創建 UserProfile
        user_profile = db.session.query(UserProfile).filter_by(user_id=user_id).first()
        if not user_profile:
            # 如果不存在 UserProfile，創建一個
            user_profile = UserProfile(
                user_id=user_id,
                display_name=display_name,
                is_online=True,
                last_seen=datetime.now(timezone.utc),
                join_date=datetime.now(timezone.utc)
                # 不需要手動設定 AuditMixin 欄位，會自動處理
            )
            db.session.add(user_profile)
        else:
            # 更新現有的 UserProfile
            user_profile.is_online = True
            user_profile.last_seen = datetime.now(timezone.utc)
            user_profile.changed_on = datetime.now(timezone.utc)
            # 不需要手動設定 changed_by_fk，AuditMixin 會自動處理
        
        db.session.commit()
        print(f"已更新使用者 {username} 的線上狀態為上線")
    except Exception as e:
        print(f"更新線上狀態失敗: {e}")
        db.session.rollback()
    
    # 加入預設房間
    join_room('general')
    
    print(f"使用者 {display_name} ({username}) 已連接, SID: {request.sid}")
    
    # 廣播使用者上線
    emit('user_joined', {
        'user_id': user_id,
        'username': username,
        'display_name': display_name,
        'message': f'{display_name} 加入聊天室'
    }, room='general')
    
    # 發送線上使用者列表（去重）
    unique_users = {}
    for user_info in online_users.values():
        user_id = user_info['user_id']
        unique_users[user_id] = user_info
    
    print(f"Socket記憶體中總連接數: {len(online_users)}, 去重後使用者數: {len(unique_users)}")
    emit('online_users', list(unique_users.values()), room='general')

@socketio.on('disconnect')
def on_disconnect(auth=None):
    """使用者斷線"""
    if request.sid in online_users:
        user_info = online_users[request.sid]
        user_id = user_info['user_id']
        username = user_info['username']
        display_name = user_info['display_name']
        
        # 檢查該使用者是否還有其他活躍的連接
        other_connections = False
        for sid, info in online_users.items():
            if sid != request.sid and info['user_id'] == user_id:
                other_connections = True
                break
        
        # 移除線上使用者記錄
        del online_users[request.sid]
        
        # 只有當用戶沒有其他活躍連接時，才更新資料庫為離線狀態
        if not other_connections:
            print(f"準備將使用者 {username} (ID: {user_id}) 設為離線狀態")
            try:
                # 確保 user_id 是有效的整數
                if user_id is None:
                    print(f"❌ user_id 為 None，無法更新資料庫")
                    return
                
                print(f"🔍 DEBUG: user_id = {user_id}, type = {type(user_id)}")
                
                # 獲取使用者物件並設定到 Flask g 對象，這樣 AuditMixin 才能正確取得 user_id
                User = appbuilder.sm.user_model
                user_obj = db.session.query(User).filter_by(id=user_id).first()
                if not user_obj:
                    print(f"❌ 找不到 User 物件 (ID: {user_id})")
                    return
                
                # 設定 Flask g.user，這樣 AuditMixin.get_user_id() 就能正確返回 user_id
                g.user = user_obj
                print(f"🔍 DEBUG: 已設定 g.user = {g.user.username} (ID: {g.user.id})")
                
                user_profile = db.session.query(UserProfile).filter_by(user_id=user_id).first()
                if user_profile:
                    print(f"找到使用者資料: {user_profile.display_name}, 目前線上狀態: {user_profile.is_online}")
                    
                    user_profile.is_online = False
                    user_profile.last_seen = datetime.now(timezone.utc)
                    user_profile.changed_on = datetime.now(timezone.utc)
                    # 不需要手動設定 changed_by_fk，AuditMixin 會自動處理
                    
                    print(f"🔍 DEBUG: 提交前 changed_by_fk = {user_profile.changed_by_fk}")
                    db.session.commit()
                    print(f"✅ 已成功更新使用者 {username} 的線上狀態為離線，last_seen: {user_profile.last_seen}")
                else:
                    print(f"❌ 找不到使用者 {username} (ID: {user_id}) 的 UserProfile 記錄")
            except Exception as e:
                print(f"❌ 更新離線狀態失敗: {e}")
                import traceback
                traceback.print_exc()
                db.session.rollback()
        else:
            print(f"使用者 {username} 還有其他活躍連接，不更新資料庫狀態")
        
        print(f"使用者 {display_name} 已斷線, SID: {request.sid}")
        
        # 廣播使用者離線（只有在沒有其他連接時才廣播）
        if not other_connections:
            emit('user_left', {
                'user_id': user_id,
                'username': username,
                'display_name': display_name,
                'message': f'{display_name} 離開聊天室'
            }, room='general')
        
        # 更新線上使用者列表（去重）
        unique_users = {}
        for user_info in online_users.values():
            user_id = user_info['user_id']
            unique_users[user_id] = user_info
        
        print(f"斷線後Socket記憶體中總連接數: {len(online_users)}, 去重後使用者數: {len(unique_users)}")
        emit('online_users', list(unique_users.values()), room='general')

@socketio.on('send_message')
def handle_message(data):
    """處理發送訊息"""
    # 從 online_users 中取得使用者資訊（因為 Socket.IO 可能無法直接使用 current_user）
    user_info = online_users.get(request.sid)
    if not user_info:
        emit('error', {'message': '未認證使用者'})
        return
    
    content = data.get('content', '').strip()
    if not content:
        emit('error', {'message': '訊息內容不能為空'})
        return
    
    # 獲取頻道ID
    channel_id = data.get('channel_id')
    if not channel_id:
        emit('error', {'message': '必須指定頻道ID'})
        return
    
    user_id = user_info['user_id']
    username = user_info['username']
    display_name = user_info['display_name']
    
    # 儲存訊息到資料庫
    try:
        # 取得使用者物件以便設定 AuditMixin 欄位
        User = appbuilder.sm.user_model
        user = db.session.query(User).filter_by(id=user_id).first()
        
        if not user:
            emit('error', {'message': '使用者不存在'})
            return
        
        new_message = ChatMessage(
            content=content,
            sender_id=user_id,
            channel_id=channel_id,  # 使用前端傳遞的頻道ID
            # 手動設定 AuditMixin 欄位
            created_by_fk=user_id,
            changed_by_fk=user_id,
            created_on=datetime.now(timezone.utc),
            changed_on=datetime.now(timezone.utc)
        )
        
        db.session.add(new_message)
        db.session.commit()
        
        # 準備廣播資料（使用 ISO 8601 UTC 格式）
        message_data = {
            'id': new_message.id,
            'content': content,
            'sender_id': user_id,
            'sender_name': display_name,
            'created_on': to_iso_utc(new_message.created_on),
            'channel_id': new_message.channel_id
        }
        
        print(f"新訊息來自 {display_name}: {content}")
        
        # 廣播訊息到所有連線使用者
        emit('new_message', message_data, room='general')
        
    except Exception as e:
        print(f"儲存訊息失敗: {e}")
        db.session.rollback()
        emit('error', {'message': '發送訊息失敗'})

@socketio.on('delete_message')
def handle_delete_message(data):
    """處理刪除訊息"""
    # 從 online_users 中取得使用者資訊（因為 Socket.IO 可能無法直接使用 current_user）
    user_info = online_users.get(request.sid)
    if not user_info:
        emit('error', {'message': '未認證使用者'})
        return
    
    message_id = data.get('message_id')
    if not message_id:
        emit('error', {'message': '無效的訊息ID'})
        return
    
    user_id = user_info['user_id']
    username = user_info['username']
    
    try:
        # 查找訊息
        message = db.session.query(ChatMessage).filter_by(
            id=message_id,
            sender_id=user_id
        ).first()
        
        if not message:
            emit('error', {'message': '找不到訊息或無權限刪除'})
            return
        
        channel_id = message.channel_id
        
        # 刪除訊息
        db.session.delete(message)
        db.session.commit()
        
        print(f"使用者 {username} 刪除了訊息 ID: {message_id}")
        
        # 廣播刪除事件
        emit('message_deleted', {
            'message_id': message_id, 
            'channel_id': channel_id
        }, room='general')
        
    except Exception as e:
        print(f"刪除訊息失敗: {e}")
        db.session.rollback()
        emit('error', {'message': '刪除訊息失敗'})

@socketio.on('typing')
def handle_typing(data):
    """處理輸入狀態"""
    # 從 online_users 中取得使用者資訊
    user_info = online_users.get(request.sid)
    if not user_info:
        return
    
    is_typing = data.get('is_typing', False)
    user_id = user_info['user_id']
    display_name = user_info['display_name']
    
    # 廣播輸入狀態（除了自己）
    emit('user_typing', {
        'user_id': user_id,
        'display_name': display_name,
        'is_typing': is_typing
    }, room='general', include_self=False)

@socketio.on('join_room')
def handle_join_room(data):
    """加入特定房間"""
    # 從 online_users 中取得使用者資訊
    user_info = online_users.get(request.sid)
    if not user_info:
        return
    
    room = data.get('room', 'general')
    join_room(room)
    
    display_name = user_info['display_name']
    emit('status', {'message': f'{display_name} 已加入房間 {room}'}, room=room)

@socketio.on('leave_room')
def handle_leave_room(data):
    """離開特定房間"""
    # 從 online_users 中取得使用者資訊
    user_info = online_users.get(request.sid)
    if not user_info:
        return
    
    room = data.get('room', 'general')
    leave_room(room)
    
    display_name = user_info['display_name']
    emit('status', {'message': f'{display_name} 已離開房間 {room}'}, room=room)

@socketio.on('get_online_users')
def handle_get_online_users():
    """取得線上使用者列表"""
    # 去重後發送
    unique_users = {}
    for user_info in online_users.values():
        user_id = user_info['user_id']
        unique_users[user_id] = user_info
    
    emit('online_users', list(unique_users.values()))

# 錯誤處理
@socketio.on_error_default
def default_error_handler(e):
    print(f"SocketIO 錯誤: {e}")
    emit('error', {'message': '伺服器發生錯誤'})