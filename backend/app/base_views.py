from flask_appbuilder import BaseView
from flask_login import current_user
from . import db
from .models import ChatRoom, RoomMember


class ChatBaseView(BaseView):
    """聊天系統的基礎視圖類，提供共用的功能"""
    
    def _get_current_user(self):
        """獲取當前登入的 Flask-AppBuilder 用戶"""
        if not current_user or not current_user.is_authenticated:
            return None
        return current_user
    
    def _check_room_access(self, user, room_id):
        """檢查用戶是否有聊天室存取權限"""
        if not user:
            return False
        room = db.session.query(ChatRoom).get(room_id)
        if not room:
            return False
        # 公開聊天室或用戶是成員
        if not room.is_private:
            return True
        return db.session.query(RoomMember).filter_by(
            room_id=room_id, user_id=user.id
        ).first() is not None
    
    def _is_room_admin(self, user, room_id):
        """檢查用戶是否為聊天室管理員"""
        if not user:
            return False
        member = db.session.query(RoomMember).filter_by(
            room_id=room_id, 
            user_id=user.id,
            is_admin=True
        ).first()
        return member is not None
    
    def _is_room_creator(self, user, room_id):
        """檢查用戶是否為聊天室創建者"""
        if not user:
            return False
        room = db.session.query(ChatRoom).get(room_id)
        return room and room.created_by == user.id
    
    def _check_admin_permission(self, user, room_id):
        """檢查用戶是否有管理權限（管理員或創建者）"""
        return self._is_room_admin(user, room_id) or self._is_room_creator(user, room_id)