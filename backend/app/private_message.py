from flask import request, jsonify, session
from flask_appbuilder import BaseView, expose, has_access
from flask_appbuilder.security.decorators import protect
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_
from datetime import datetime
from . import db, appbuilder
from .models import PrivateMessage, UserStatus
from flask_appbuilder.security.sqla.models import User
from .base_views import ChatBaseView


class PrivateMessageView(ChatBaseView):
    route_base = '/private'
    default_view = 'send_private_message'
    base_permissions = ['can_send', 'can_read', 'can_mark_read']
    
    @expose('/send', methods=['POST'])
    @has_access
    def send_private_message(self):
        try:
            current_user_obj = self._get_current_user()
            if not current_user_obj:
                return jsonify({'error': '請先登入'}), 401
            
            data = request.get_json()
            if not data or 'receiver_id' not in data or 'content' not in data:
                return jsonify({'error': '缺少必要欄位'}), 400
            
            receiver_id = data['receiver_id']
            content = data['content']
            message_type = data.get('message_type', 'text')
            
            # 檢查接收者是否存在
            receiver = db.session.query(User).get(receiver_id)
            if not receiver:
                return jsonify({'error': '接收者不存在'}), 404
            
            # 不能發私訊給自己
            if receiver_id == current_user_obj.id:
                return jsonify({'error': '不能發私訊給自己'}), 400
            
            # 創建私訊
            new_message = PrivateMessage(
                sender_id=current_user_obj.id,
                receiver_id=receiver_id,
                content=content,
                message_type=message_type
            )
            
            db.session.add(new_message)
            db.session.commit()
            
            return jsonify({
                'message': '私訊發送成功',
                'data': {
                    'id': new_message.id,
                    'sender': current_user_obj.username,
                    'receiver': receiver.username,
                    'content': new_message.content,
                    'message_type': new_message.message_type,
                    'created_at': new_message.created_at.isoformat()
                }
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @expose('/conversations', methods=['GET'])
    def get_conversations(self):
        try:
            current_user_obj = self._get_current_user()
            if not current_user_obj:
                return jsonify({'error': '請先登入'}), 401
            
            # 獲取對話列表 - 找出所有與當前用戶有私訊往來的用戶
            conversations_query = db.session.query(
                User.id,
                User.username,
                User.email,
                PrivateMessage.created_at,
                PrivateMessage.content,
                PrivateMessage.sender_id,
                PrivateMessage.is_read
            ).join(
                PrivateMessage,
                or_(
                    and_(User.id == PrivateMessage.sender_id, PrivateMessage.receiver_id == current_user_obj.id),
                    and_(User.id == PrivateMessage.receiver_id, PrivateMessage.sender_id == current_user_obj.id)
                )
            ).filter(
                and_(
                    or_(
                        PrivateMessage.is_deleted_by_sender == False,
                        PrivateMessage.sender_id != current_user_obj.id
                    ),
                    or_(
                        PrivateMessage.is_deleted_by_receiver == False,
                        PrivateMessage.receiver_id != current_user_obj.id
                    )
                )
            ).order_by(PrivateMessage.created_at.desc()).all()
            
            # 整理對話列表，每個用戶只顯示最新一條訊息
            conversations = {}
            for conv in conversations_query:
                user_id, username, email, created_at, content, sender_id, is_read = conv
                
                if user_id not in conversations:
                    # 計算未讀訊息數
                    unread_count = db.session.query(PrivateMessage).filter(
                        PrivateMessage.sender_id == user_id,
                        PrivateMessage.receiver_id == current_user_obj.id,
                        PrivateMessage.is_read == False,
                        PrivateMessage.is_deleted_by_receiver == False
                    ).count()
                    
                    conversations[user_id] = {
                        'user_id': user_id,
                        'username': username,
                        'email': email,
                        'last_message': content,
                        'last_message_time': created_at.isoformat(),
                        'is_sender': sender_id == current_user_obj.id,
                        'unread_count': unread_count
                    }
            
            conversations_list = list(conversations.values())
            conversations_list.sort(key=lambda x: x['last_message_time'], reverse=True)
            
            return jsonify({'conversations': conversations_list}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @expose('/messages/<int:other_user_id>', methods=['GET'])
    def get_messages_with_user(self, other_user_id):
        try:
            current_user_obj = self._get_current_user()
            if not current_user_obj:
                return jsonify({'error': '請先登入'}), 401
            
            # 檢查對方用戶是否存在
            other_user = db.session.query(User).get(other_user_id)
            if not other_user:
                return jsonify({'error': '用戶不存在'}), 404
            
            # 分頁參數
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 50, type=int), 100)
            
            # 獲取兩人之間的私訊 (按時間倒序)
            messages_query = db.session.query(PrivateMessage).filter(
                or_(
                    and_(
                        PrivateMessage.sender_id == current_user_obj.id,
                        PrivateMessage.receiver_id == other_user_id,
                        PrivateMessage.is_deleted_by_sender == False
                    ),
                    and_(
                        PrivateMessage.sender_id == other_user_id,
                        PrivateMessage.receiver_id == current_user_obj.id,
                        PrivateMessage.is_deleted_by_receiver == False
                    )
                )
            ).order_by(PrivateMessage.created_at.desc())
            
            paginated_messages = messages_query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            messages_data = []
            for message in paginated_messages.items:
                messages_data.append({
                    'id': message.id,
                    'sender_id': message.sender_id,
                    'receiver_id': message.receiver_id,
                    'content': message.content,
                    'message_type': message.message_type,
                    'is_read': message.is_read,
                    'is_sender': message.sender_id == current_user_obj.id,
                    'created_at': message.created_at.isoformat()
                })
            
            # 標記對方發送給我的未讀訊息為已讀
            db.session.query(PrivateMessage).filter(
                PrivateMessage.sender_id == other_user_id,
                PrivateMessage.receiver_id == current_user_obj.id,
                PrivateMessage.is_read == False
            ).update({'is_read': True})
            db.session.commit()
            
            return jsonify({
                'other_user': {
                    'id': other_user.id,
                    'username': other_user.username,
                    'email': other_user.email
                },
                'messages': messages_data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': paginated_messages.total,
                    'pages': paginated_messages.pages,
                    'has_next': paginated_messages.has_next,
                    'has_prev': paginated_messages.has_prev
                }
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @expose('/delete/<int:message_id>', methods=['DELETE'])
    def delete_private_message(self, message_id):
        try:
            current_user_obj = self._get_current_user()
            if not current_user_obj:
                return jsonify({'error': '請先登入'}), 401
            
            message = db.session.query(PrivateMessage).get(message_id)
            if not message:
                return jsonify({'error': '訊息不存在'}), 404
            
            # 檢查權限 - 只有發送者和接收者可以刪除
            if message.sender_id != current_user_obj.id and message.receiver_id != current_user_obj.id:
                return jsonify({'error': '無權限刪除此訊息'}), 403
            
            # 軟刪除 - 根據用戶身份設置對應的刪除標記
            if message.sender_id == current_user_obj.id:
                message.is_deleted_by_sender = True
            else:
                message.is_deleted_by_receiver = True
            
            db.session.commit()
            
            return jsonify({'message': '訊息已刪除'}), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @expose('/mark_read/<int:message_id>', methods=['PUT'])
    def mark_message_read(self, message_id):
        try:
            current_user_obj = self._get_current_user()
            if not current_user_obj:
                return jsonify({'error': '請先登入'}), 401
            
            message = db.session.query(PrivateMessage).get(message_id)
            if not message:
                return jsonify({'error': '訊息不存在'}), 404
            
            # 只有接收者可以標記為已讀
            if message.receiver_id != current_user_obj.id:
                return jsonify({'error': '只能標記接收到的訊息為已讀'}), 403
            
            message.is_read = True
            db.session.commit()
            
            return jsonify({'message': '訊息已標記為已讀'}), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500


class UserStatusView(ChatBaseView):
    route_base = '/status'
    default_view = 'update_status'
    base_permissions = ['can_update', 'can_view']
    
    @expose('/update', methods=['PUT'])
    @has_access
    def update_status(self):
        try:
            current_user_obj = self._get_current_user()
            if not current_user_obj:
                return jsonify({'error': '請先登入'}), 401
            
            data = request.get_json()
            if not data:
                return jsonify({'error': '無資料'}), 400
            
            status = data.get('status', 'online')
            status_message = data.get('status_message', '')
            
            # 檢查或創建用戶狀態
            user_status = db.session.query(UserStatus).filter_by(user_id=current_user_obj.id).first()
            if not user_status:
                user_status = UserStatus(user_id=current_user_obj.id)
                db.session.add(user_status)
            
            user_status.status = status
            user_status.status_message = status_message
            user_status.last_seen = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'message': '狀態更新成功',
                'status': {
                    'status': user_status.status,
                    'status_message': user_status.status_message,
                    'last_seen': user_status.last_seen.isoformat()
                }
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @expose('/users', methods=['GET'])
    @has_access
    def get_online_users(self):
        try:
            current_user_obj = self._get_current_user()
            if not current_user_obj:
                return jsonify({'error': '請先登入'}), 401
            
            # 獲取所有用戶及其狀態
            users_query = db.session.query(
                User.id,
                User.username,
                User.email,
                UserStatus.status,
                UserStatus.status_message,
                UserStatus.last_seen
            ).outerjoin(UserStatus, User.id == UserStatus.user_id).all()
            
            users_data = []
            for user_data in users_query:
                user_id, username, email, status, status_message, last_seen = user_data
                
                if user_id != current_user_obj.id:  # 不包含當前用戶
                    users_data.append({
                        'id': user_id,
                        'username': username,
                        'email': email,
                        'status': status or 'offline',
                        'status_message': status_message or '',
                        'last_seen': last_seen.isoformat() if last_seen else None
                    })
            
            return jsonify({'users': users_data}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500