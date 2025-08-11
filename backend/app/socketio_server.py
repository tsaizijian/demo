from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user
from flask_jwt_extended import decode_token, get_jwt_identity
from datetime import datetime
import jwt

from . import app, db, appbuilder
from .models import ChatMessage

socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000", 
                   logger=True, engineio_logger=True)

# 儲存線上使用者
online_users = {}

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
    
    # 記錄新的線上使用者
    online_users[request.sid] = {
        'user_id': user_id,
        'username': username,
        'display_name': display_name,
        'connected_at': datetime.now().isoformat()
    }
    
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
    
    # 發送線上使用者列表
    emit('online_users', list(online_users.values()), room='general')

@socketio.on('disconnect')
def on_disconnect():
    """使用者斷線"""
    if request.sid in online_users:
        user_info = online_users[request.sid]
        display_name = user_info['display_name']
        
        # 移除線上使用者記錄
        del online_users[request.sid]
        
        print(f"使用者 {display_name} 已斷線, SID: {request.sid}")
        
        # 廣播使用者離線
        emit('user_left', {
            'user_id': user_info['user_id'],
            'username': user_info['username'],
            'display_name': display_name,
            'message': f'{display_name} 離開聊天室'
        }, room='general')
        
        # 更新線上使用者列表
        emit('online_users', list(online_users.values()), room='general')

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
            channel_id=1,  # 預設頻道
            # 手動設定 AuditMixin 欄位
            created_by_fk=user_id,
            changed_by_fk=user_id,
            created_on=datetime.utcnow(),
            changed_on=datetime.utcnow()
        )
        
        db.session.add(new_message)
        db.session.commit()
        
        # 準備廣播資料
        message_data = {
            'id': new_message.id,
            'content': content,
            'sender_id': user_id,
            'sender_name': display_name,
            'created_on': new_message.created_on.isoformat(),
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
    if not current_user or not current_user.is_authenticated:
        emit('error', {'message': '未認證使用者'})
        return
    
    message_id = data.get('message_id')
    if not message_id:
        emit('error', {'message': '無效的訊息ID'})
        return
    
    try:
        # 查找訊息
        message = db.session.query(ChatMessage).filter_by(
            id=message_id,
            sender_id=current_user.id
        ).first()
        
        if not message:
            emit('error', {'message': '找不到訊息或無權限刪除'})
            return
        
        # 刪除訊息
        db.session.delete(message)
        db.session.commit()
        
        print(f"使用者 {current_user.username} 刪除了訊息 ID: {message_id}")
        
        # 廣播刪除事件
        emit('message_deleted', {'message_id': message_id}, room='general')
        
    except Exception as e:
        print(f"刪除訊息失敗: {e}")
        db.session.rollback()
        emit('error', {'message': '刪除訊息失敗'})

@socketio.on('typing')
def handle_typing(data):
    """處理輸入狀態"""
    if not current_user or not current_user.is_authenticated:
        return
    
    is_typing = data.get('is_typing', False)
    display_name = getattr(current_user, 'first_name', None) or current_user.username
    
    # 廣播輸入狀態（除了自己）
    emit('user_typing', {
        'user_id': current_user.id,
        'display_name': display_name,
        'is_typing': is_typing
    }, room='general', include_self=False)

@socketio.on('join_room')
def handle_join_room(data):
    """加入特定房間"""
    room = data.get('room', 'general')
    join_room(room)
    
    if current_user and current_user.is_authenticated:
        display_name = getattr(current_user, 'first_name', None) or current_user.username
        emit('status', {'message': f'{display_name} 已加入房間 {room}'}, room=room)

@socketio.on('leave_room')
def handle_leave_room(data):
    """離開特定房間"""
    room = data.get('room', 'general')
    leave_room(room)
    
    if current_user and current_user.is_authenticated:
        display_name = getattr(current_user, 'first_name', None) or current_user.username
        emit('status', {'message': f'{display_name} 已離開房間 {room}'}, room=room)

@socketio.on('get_online_users')
def handle_get_online_users():
    """取得線上使用者列表"""
    emit('online_users', list(online_users.values()))

# 錯誤處理
@socketio.on_error_default
def default_error_handler(e):
    print(f"SocketIO 錯誤: {e}")
    emit('error', {'message': '伺服器發生錯誤'})