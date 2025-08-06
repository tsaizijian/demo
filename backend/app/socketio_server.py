from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user
from datetime import datetime

from . import app, db, appbuilder
from .models import ChatMessage

socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000", 
                   logger=True, engineio_logger=True)

# 儲存線上使用者
online_users = {}

@socketio.on('connect')
def on_connect():
    """使用者連接"""
    if not current_user or not current_user.is_authenticated:
        print(f"未認證使用者嘗試連接: {request.sid}")
        return False
    
    user_id = current_user.id
    username = current_user.username
    display_name = getattr(current_user, 'first_name', None) or username
    
    # 記錄線上使用者
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
    if not current_user or not current_user.is_authenticated:
        emit('error', {'message': '未認證使用者'})
        return
    
    content = data.get('content', '').strip()
    if not content:
        emit('error', {'message': '訊息內容不能為空'})
        return
    
    user_id = current_user.id
    username = current_user.username
    display_name = getattr(current_user, 'first_name', None) or username
    
    # 儲存訊息到資料庫
    try:
        new_message = ChatMessage(
            content=content,
            sender_id=user_id,
            channel_id=1  # 預設頻道
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