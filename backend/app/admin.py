from flask import request, jsonify, session
from flask_appbuilder import expose, has_access
from flask_appbuilder.security.decorators import protect
from . import db, appbuilder
from .models import ChatRoom, RoomMember, Message
from flask_appbuilder.security.sqla.models import User
from .base_views import ChatBaseView


class AdminView(ChatBaseView):
    route_base = '/admin'
    default_view = 'kick_user_from_room'
    base_permissions = ['can_kick', 'can_promote', 'can_demote', 'can_delete', 'can_ban', 'can_update']
    
    
    @expose('/room/<int:room_id>/kick/<int:user_id>', methods=['POST'])
    @has_access
    def kick_user_from_room(self, room_id, user_id):
        try:
            current_user_obj = self._get_current_user()
            if not current_user_obj:
                return jsonify({'error': '請先登入'}), 401
            
            # 檢查是否為聊天室管理員或創建者
            if not self._check_admin_permission(current_user_obj, room_id):
                return jsonify({'error': '沒有管理權限'}), 403
            
            # 檢查目標用戶是否在聊天室中
            target_member = db.session.query(RoomMember).filter_by(
                room_id=room_id, 
                user_id=user_id
            ).first()
            
            if not target_member:
                return jsonify({'error': '用戶不在此聊天室中'}), 404
            
            # 不能踢除自己
            if user_id == current_user_obj.id:
                return jsonify({'error': '不能踢除自己'}), 400
            
            # 獲取目標用戶資訊
            target_user = db.session.query(User).get(user_id)
            
            # 踢除用戶
            db.session.delete(target_member)
            db.session.commit()
            
            return jsonify({
                'message': f'用戶 {target_user.username} 已被踢出聊天室'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @expose('/room/<int:room_id>/promote/<int:user_id>', methods=['POST'])
    @has_access
    def promote_to_admin(self, room_id, user_id):
        try:
            current_user_obj = self._get_current_user()
            if not current_user_obj:
                return jsonify({'error': '請先登入'}), 401
            
            # 只有創建者可以提升管理員
            if not self._is_room_creator(current_user_obj, room_id):
                return jsonify({'error': '只有聊天室創建者可以提升管理員'}), 403
            
            # 檢查目標用戶是否在聊天室中
            target_member = db.session.query(RoomMember).filter_by(
                room_id=room_id, 
                user_id=user_id
            ).first()
            
            if not target_member:
                return jsonify({'error': '用戶不在此聊天室中'}), 404
            
            # 檢查是否已經是管理員
            if target_member.is_admin:
                return jsonify({'error': '用戶已經是管理員'}), 400
            
            # 獲取目標用戶資訊
            target_user = db.session.query(User).get(user_id)
            
            # 提升為管理員
            target_member.is_admin = True
            db.session.commit()
            
            return jsonify({
                'message': f'用戶 {target_user.username} 已被提升為管理員'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @expose('/room/<int:room_id>/demote/<int:user_id>', methods=['POST'])
    @has_access
    def demote_admin(self, room_id, user_id):
        try:
            current_user_obj = self._get_current_user()
            if not current_user_obj:
                return jsonify({'error': '請先登入'}), 401
            
            # 只有創建者可以降級管理員
            if not self._is_room_creator(current_user_obj, room_id):
                return jsonify({'error': '只有聊天室創建者可以降級管理員'}), 403
            
            # 檢查目標用戶是否在聊天室中
            target_member = db.session.query(RoomMember).filter_by(
                room_id=room_id, 
                user_id=user_id
            ).first()
            
            if not target_member:
                return jsonify({'error': '用戶不在此聊天室中'}), 404
            
            # 檢查是否為管理員
            if not target_member.is_admin:
                return jsonify({'error': '用戶不是管理員'}), 400
            
            # 不能降級自己
            if user_id == current_user_obj.id:
                return jsonify({'error': '不能降級自己'}), 400
            
            # 獲取目標用戶資訊
            target_user = db.session.query(User).get(user_id)
            
            # 降級管理員
            target_member.is_admin = False
            db.session.commit()
            
            return jsonify({
                'message': f'用戶 {target_user.username} 的管理員權限已被撤銷'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @expose('/room/<int:room_id>/delete', methods=['DELETE'])
    @has_access
    def delete_room(self, room_id):
        try:
            current_user_obj = self._get_current_user()
            if not current_user_obj:
                return jsonify({'error': '請先登入'}), 401
            
            room = db.session.query(ChatRoom).get(room_id)
            if not room:
                return jsonify({'error': '聊天室不存在'}), 404
            
            # 只有創建者可以刪除聊天室
            if room.created_by != current_user_obj.id:
                return jsonify({'error': '只有聊天室創建者可以刪除聊天室'}), 403
            
            room_name = room.name
            
            # 刪除相關資料 (級聯刪除)
            # 先刪除訊息附件
            message_ids = [msg.id for msg in room.messages]
            if message_ids:
                from .models import MessageAttachment
                db.session.query(MessageAttachment).filter(
                    MessageAttachment.message_id.in_(message_ids)
                ).delete(synchronize_session=False)
            
            # 刪除訊息
            db.session.query(Message).filter_by(room_id=room_id).delete()
            
            # 刪除成員關係
            db.session.query(RoomMember).filter_by(room_id=room_id).delete()
            
            # 刪除聊天室
            db.session.delete(room)
            db.session.commit()
            
            return jsonify({
                'message': f'聊天室 "{room_name}" 已被刪除'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @expose('/room/<int:room_id>/update', methods=['PUT'])
    @has_access
    def update_room_info(self, room_id):
        try:
            current_user_obj = self._get_current_user()
            if not current_user_obj:
                return jsonify({'error': '請先登入'}), 401
            
            room = db.session.query(ChatRoom).get(room_id)
            if not room:
                return jsonify({'error': '聊天室不存在'}), 404
            
            # 檢查是否為管理員或創建者
            if not (self._is_room_admin(current_user_obj, room_id) or self._is_room_creator(current_user_obj, room_id)):
                return jsonify({'error': '沒有管理權限'}), 403
            
            data = request.get_json()
            if not data:
                return jsonify({'error': '無資料'}), 400
            
            # 更新聊天室資訊
            if 'name' in data:
                room.name = data['name']
            if 'description' in data:
                room.description = data['description']
            if 'is_private' in data and self._is_room_creator(current_user_obj, room_id):
                # 只有創建者可以更改私密性
                room.is_private = data['is_private']
            
            db.session.commit()
            
            return jsonify({
                'message': '聊天室資訊已更新',
                'room': {
                    'id': room.id,
                    'name': room.name,
                    'description': room.description,
                    'is_private': room.is_private
                }
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @expose('/message/<int:message_id>/delete', methods=['DELETE'])
    @has_access
    def admin_delete_message(self, message_id):
        try:
            current_user_obj = self._get_current_user()
            if not current_user_obj:
                return jsonify({'error': '請先登入'}), 401
            
            message = db.session.query(Message).get(message_id)
            if not message:
                return jsonify({'error': '訊息不存在'}), 404
            
            # 檢查是否為聊天室管理員或創建者
            if not (self._is_room_admin(current_user_obj, message.room_id) or self._is_room_creator(current_user_obj, message.room_id)):
                return jsonify({'error': '沒有管理權限'}), 403
            
            # 軟刪除訊息
            message.is_deleted = True
            db.session.commit()
            
            return jsonify({'message': '訊息已被管理員刪除'}), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @expose('/room/<int:room_id>/ban/<int:user_id>', methods=['POST'])
    @has_access
    def ban_user_from_room(self, room_id, user_id):
        """禁止用戶加入聊天室 (創建黑名單功能的基礎)"""
        try:
            current_user_obj = self._get_current_user()
            if not current_user_obj:
                return jsonify({'error': '請先登入'}), 401
            
            # 檢查是否為創建者
            if not self._is_room_creator(current_user_obj, room_id):
                return jsonify({'error': '只有聊天室創建者可以禁止用戶'}), 403
            
            # 先踢出用戶 (如果在聊天室中)
            target_member = db.session.query(RoomMember).filter_by(
                room_id=room_id, 
                user_id=user_id
            ).first()
            
            if target_member:
                db.session.delete(target_member)
            
            # 這裡可以擴展為創建黑名單表
            # 目前只是踢出用戶
            db.session.commit()
            
            target_user = db.session.query(User).get(user_id)
            return jsonify({
                'message': f'用戶 {target_user.username} 已被禁止進入聊天室'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500