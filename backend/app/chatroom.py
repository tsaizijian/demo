from flask import request, jsonify, session
from flask_appbuilder import expose, has_access
from flask_appbuilder.security.decorators import protect
from . import db, appbuilder
from .models import ChatRoom, RoomMember
from flask_appbuilder.security.sqla.models import User
from .base_views import ChatBaseView


class ChatRoomManageView(ChatBaseView):
    route_base = '/chatroom'
    default_view = 'list_rooms'
    base_permissions = ['can_create', 'can_join', 'can_leave', 'can_list']
    
    
    @expose('/create', methods=['POST'])
    @has_access
    def create_room(self):
        try:
            current_user_obj = self._get_current_user()
            if not current_user_obj:
                return jsonify({'error': '請先登入'}), 401
            
            data = request.get_json()
            if not data or 'name' not in data:
                return jsonify({'error': '聊天室名稱不能為空'}), 400
            
            name = data['name']
            description = data.get('description', '')
            is_private = data.get('is_private', False)
            
            new_room = ChatRoom(
                name=name,
                description=description,
                is_private=is_private,
                created_by=current_user_obj.id
            )
            
            db.session.add(new_room)
            db.session.flush()
            
            # 自動將創建者加入聊天室並設為管理員
            creator_member = RoomMember(
                room_id=new_room.id,
                user_id=current_user_obj.id,
                is_admin=True
            )
            db.session.add(creator_member)
            db.session.commit()
            
            return jsonify({
                'message': '聊天室創建成功',
                'room': {
                    'id': new_room.id,
                    'name': new_room.name,
                    'description': new_room.description,
                    'is_private': new_room.is_private,
                    'created_by': current_user_obj.username,
                    'created_at': new_room.created_at.isoformat()
                }
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @expose('/list', methods=['GET'])
    @has_access
    def list_rooms(self):
        try:
            current_user_obj = self._get_current_user()
            if not current_user_obj:
                return jsonify({'error': '請先登入'}), 401
            
            # 獲取公開聊天室和用戶已加入的私密聊天室
            public_rooms = db.session.query(ChatRoom).filter_by(is_private=False).all()
            
            # 獲取用戶已加入的聊天室
            user_rooms_query = db.session.query(ChatRoom).join(RoomMember).filter(
                RoomMember.user_id == current_user_obj.id
            ).all()
            
            # 合併並去重
            all_rooms = list({room.id: room for room in public_rooms + user_rooms_query}.values())
            
            rooms_data = []
            for room in all_rooms:
                # 檢查用戶是否為成員
                is_member = db.session.query(RoomMember).filter_by(room_id=room.id, user_id=current_user_obj.id).first() is not None
                member_count = db.session.query(RoomMember).filter_by(room_id=room.id).count()
                
                rooms_data.append({
                    'id': room.id,
                    'name': room.name,
                    'description': room.description,
                    'is_private': room.is_private,
                    'member_count': member_count,
                    'is_member': is_member,
                    'created_at': room.created_at.isoformat()
                })
            
            return jsonify({'rooms': rooms_data}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @expose('/join/<int:room_id>', methods=['POST'])
    @has_access
    def join_room(self, room_id):
        try:
            current_user_obj = self._get_current_user()
            if not current_user_obj:
                return jsonify({'error': '請先登入'}), 401
            
            room = db.session.query(ChatRoom).get(room_id)
            if not room:
                return jsonify({'error': '聊天室不存在'}), 404
            
            # 檢查是否已經是成員
            existing_member = db.session.query(RoomMember).filter_by(room_id=room_id, user_id=current_user_obj.id).first()
            if existing_member:
                return jsonify({'error': '已經是聊天室成員'}), 409
            
            new_member = RoomMember(
                room_id=room_id,
                user_id=current_user_obj.id,
                is_admin=False
            )
            
            db.session.add(new_member)
            db.session.commit()
            
            return jsonify({'message': f'成功加入聊天室 "{room.name}"'}), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @expose('/leave/<int:room_id>', methods=['POST'])
    @has_access
    def leave_room(self, room_id):
        try:
            current_user_obj = self._get_current_user()
            if not current_user_obj:
                return jsonify({'error': '請先登入'}), 401
            
            room = db.session.query(ChatRoom).get(room_id)
            if not room:
                return jsonify({'error': '聊天室不存在'}), 404
            
            member = db.session.query(RoomMember).filter_by(room_id=room_id, user_id=current_user_obj.id).first()
            if not member:
                return jsonify({'error': '您不是此聊天室的成員'}), 400
            
            # 檢查是否為創建者
            if room.created_by == current_user_obj.id:
                # 檢查是否還有其他成員
                other_members = db.session.query(RoomMember).filter(
                    RoomMember.room_id == room_id,
                    RoomMember.user_id != current_user_obj.id
                ).all()
                
                if other_members:
                    # 將管理員權限轉移給第一個成員
                    other_members[0].is_admin = True
                    db.session.add(other_members[0])
            
            db.session.delete(member)
            db.session.commit()
            
            return jsonify({'message': f'已退出聊天室 "{room.name}"'}), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @expose('/members/<int:room_id>', methods=['GET'])
    @has_access
    def get_room_members(self, room_id):
        try:
            current_user_obj = self._get_current_user()
            if not current_user_obj:
                return jsonify({'error': '請先登入'}), 401
            
            room = db.session.query(ChatRoom).get(room_id)
            if not room:
                return jsonify({'error': '聊天室不存在'}), 404
            
            # 檢查用戶是否為聊天室成員
            is_member = db.session.query(RoomMember).filter_by(room_id=room_id, user_id=current_user_obj.id).first()
            if not is_member and room.is_private:
                return jsonify({'error': '無權限查看此聊天室成員'}), 403
            
            members = db.session.query(RoomMember, User).join(
                User, RoomMember.user_id == User.id
            ).filter(RoomMember.room_id == room_id).all()
            
            members_data = []
            for member, user in members:
                members_data.append({
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_admin': member.is_admin,
                    'joined_at': member.joined_at.isoformat()
                })
            
            return jsonify({
                'room_name': room.name,
                'members': members_data
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500