from flask import request, jsonify, session, send_file
from flask_appbuilder import expose, has_access
from flask_appbuilder.security.decorators import protect
import os
import uuid
from werkzeug.utils import secure_filename
from . import db
from .models import ChatRoom, RoomMember, Message, MessageAttachment
from flask_appbuilder.security.sqla.models import User
from .base_views import ChatBaseView


class MessageManageView(ChatBaseView):
    route_base = '/message'
    default_view = 'send_message'
    base_permissions = ['can_send', 'can_upload', 'can_download', 'can_view']
    
    
    @expose('/send', methods=['POST'])
    def send_message(self):
        try:
            current_chat_user = self._get_current_user()
            if not current_chat_user:
                return jsonify({'error': '請先登入'}), 401
            
            data = request.get_json()
            if not data or 'room_id' not in data or 'content' not in data:
                return jsonify({'error': '缺少必要欄位'}), 400
            
            room_id = data['room_id']
            content = data['content']
            message_type = data.get('message_type', 'text')
            
            # 檢查聊天室是否存在
            room = db.session.query(ChatRoom).get(room_id)
            if not room:
                return jsonify({'error': '聊天室不存在'}), 404
            
            # 檢查用戶是否為聊天室成員
            if not self._check_room_access(current_chat_user, room_id):
                return jsonify({'error': '您不是此聊天室的成員'}), 403
            
            # 創建訊息
            new_message = Message(
                room_id=room_id,
                user_id=current_chat_user.id,
                content=content,
                message_type=message_type
            )
            
            db.session.add(new_message)
            db.session.commit()
            
            return jsonify({
                'message': '訊息發送成功',
                'data': {
                    'id': new_message.id,
                    'room_id': new_message.room_id,
                    'sender': current_chat_user.username,
                    'content': new_message.content,
                    'message_type': new_message.message_type,
                    'created_at': new_message.created_at.isoformat()
                }
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @expose('/room/<int:room_id>', methods=['GET'])
    @has_access
    def get_messages(self, room_id):
        try:
            current_chat_user = self._get_current_user()
            if not current_chat_user:
                return jsonify({'error': '請先登入'}), 401
            
            # 檢查聊天室是否存在
            room = db.session.query(ChatRoom).get(room_id)
            if not room:
                return jsonify({'error': '聊天室不存在'}), 404
            
            # 檢查用戶是否為聊天室成員
            if not self._check_room_access(current_chat_user, room_id):
                return jsonify({'error': '您不是此聊天室的成員'}), 403
            
            # 分頁參數
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 50, type=int), 100)
            
            # 獲取訊息（按時間倒序）
            messages_query = db.session.query(Message, User).join(
                User, Message.user_id == User.id
            ).filter(
                Message.room_id == room_id,
                Message.is_deleted == False
            ).order_by(Message.created_at.desc())
            
            paginated_messages = messages_query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            messages_data = []
            for message, sender in paginated_messages.items:
                message_data = {
                    'id': message.id,
                    'sender': {
                        'id': sender.id,
                        'username': sender.username,
                        'avatar_url': sender.avatar_url
                    },
                    'content': message.content,
                    'message_type': message.message_type,
                    'created_at': message.created_at.isoformat(),
                    'attachments': []
                }
                
                # 獲取附件
                attachments = db.session.query(MessageAttachment).filter_by(message_id=message.id).all()
                for attachment in attachments:
                    message_data['attachments'].append({
                        'id': attachment.id,
                        'file_url': attachment.file_url,
                        'file_type': attachment.file_type
                    })
                
                messages_data.append(message_data)
            
            return jsonify({
                'room_name': room.name,
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
    def delete_message(self, message_id):
        try:
            current_chat_user = self._get_current_user()
            if not current_chat_user:
                return jsonify({'error': '請先登入'}), 401
            
            message = db.session.query(Message).get(message_id)
            if not message:
                return jsonify({'error': '訊息不存在'}), 404
            
            # 檢查權限（只有發送者或聊天室管理員可以刪除）
            is_sender = message.user_id == current_chat_user.id
            is_admin = db.session.query(RoomMember).filter_by(
                room_id=message.room_id, 
                user_id=current_chat_user.id, 
                is_admin=True
            ).first() is not None
            
            if not (is_sender or is_admin):
                return jsonify({'error': '無權限刪除此訊息'}), 403
            
            # 軟刪除
            message.is_deleted = True
            db.session.commit()
            
            return jsonify({'message': '訊息已刪除'}), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @expose('/upload', methods=['POST'])
    def upload_attachment(self):
        try:
            current_chat_user = self._get_current_user()
            if not current_chat_user:
                return jsonify({'error': '請先登入'}), 401
            
            if 'file' not in request.files:
                return jsonify({'error': '沒有檔案'}), 400
            
            file = request.files['file']
            message_id = request.form.get('message_id')
            
            if file.filename == '':
                return jsonify({'error': '沒有選擇檔案'}), 400
            
            if not message_id:
                return jsonify({'error': '缺少 message_id'}), 400
            
            # 檢查訊息是否存在且屬於當前用戶
            message = db.session.query(Message).filter_by(id=message_id, user_id=current_chat_user.id).first()
            if not message:
                return jsonify({'error': '訊息不存在或無權限'}), 404
            
            # 簡單的檔案類型檢查
            allowed_extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
            file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            
            if file_extension not in allowed_extensions:
                return jsonify({'error': '不支援的檔案類型'}), 400
            
            # 生成唯一的檔案名稱
            unique_filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
            
            # 創建用戶專屬的資料夾
            user_folder = os.path.join('app', 'static', 'uploads', str(current_chat_user.id))
            os.makedirs(user_folder, exist_ok=True)
            
            # 完整的檔案路徑
            file_path = os.path.join(user_folder, unique_filename)
            
            # 儲存檔案
            file.save(file_path)
            
            # 生成可存取的 URL
            file_url = f"/static/uploads/{current_chat_user.id}/{unique_filename}"
            
            attachment = MessageAttachment(
                message_id=message_id,
                file_url=file_url,
                file_type=file_extension
            )
            
            db.session.add(attachment)
            db.session.commit()
            
            return jsonify({
                'message': '檔案上傳成功',
                'attachment': {
                    'id': attachment.id,
                    'file_url': attachment.file_url,
                    'file_type': attachment.file_type,
                    'original_filename': file.filename,
                    'file_size': os.path.getsize(file_path)
                }
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @expose('/download/<int:attachment_id>', methods=['GET'])
    def download_attachment(self, attachment_id):
        try:
            current_chat_user = self._get_current_user()
            if not current_chat_user:
                return jsonify({'error': '請先登入'}), 401
            
            # 獲取附件資訊
            attachment = db.session.query(MessageAttachment).get(attachment_id)
            if not attachment:
                return jsonify({'error': '附件不存在'}), 404
            
            # 檢查附件對應的訊息權限
            message = db.session.query(Message).get(attachment.message_id)
            if not message:
                return jsonify({'error': '訊息不存在'}), 404
            
            # 檢查用戶是否為聊天室成員
            is_member = db.session.query(RoomMember).filter_by(
                room_id=message.room_id, 
                user_id=current_chat_user.id
            ).first()
            if not is_member:
                return jsonify({'error': '無權限下載此檔案'}), 403
            
            # 構建檔案路徑 (相對於當前工作目錄)
            file_path = attachment.file_url.replace('/static/', 'app/static/')
            
            if not os.path.exists(file_path):
                return jsonify({'error': f'檔案不存在: {file_path}'}), 404
            
            from flask import send_file
            return send_file(file_path, as_attachment=True)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500