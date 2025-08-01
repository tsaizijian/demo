from flask import render_template
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, ModelRestApi

from . import appbuilder, db
from .models import ChatRoom, RoomMember, Message, MessageAttachment, PrivateMessage, UserStatus
from flask_appbuilder.security.sqla.models import User
from .chatroom import ChatRoomManageView
from .message import MessageManageView
from .private_message import PrivateMessageView as PrivateMessageManageView, UserStatusView as UserStatusManageView
from .admin import AdminView
from .user_api import RegisterApi



# Using Flask-AppBuilder's built-in User model instead of custom ChatUser


class ChatRoomView(ModelView):
    datamodel = SQLAInterface(ChatRoom)
    list_columns = ['id', 'name', 'member_count', 'description', 'is_private', 'created_by', 'created_at']


    show_columns = ['id', 'name', 'member_count', 'description', 'is_private', 'created_by', 'created_at']
    search_columns = ['name', 'description']
    edit_columns = ['name', 'description', 'is_private']
    add_columns = ['name', 'description', 'is_private', 'created_by']


class RoomMemberView(ModelView):
    datamodel = SQLAInterface(RoomMember)
    list_columns = ['id', 'room_id', 'user_id', 'joined_at', 'is_admin']
    show_columns = ['id', 'room_id', 'user_id', 'joined_at', 'is_admin']
    search_columns = ['room_id', 'user_id']
    edit_columns = ['room_id', 'user_id', 'is_admin']
    add_columns = ['room_id', 'user_id', 'is_admin']



class MessageView(ModelView):
    datamodel = SQLAInterface(Message)
    list_columns = ['id', 'room_id', 'user_id', 'content', 'message_type', 'created_at', 'is_deleted']
    show_columns = ['id', 'room_id', 'user_id', 'content', 'message_type', 'created_at', 'is_deleted']
    search_columns = ['content', 'message_type']
    edit_columns = ['room_id', 'user_id', 'content', 'message_type', 'is_deleted']  
    add_columns = ['room_id', 'user_id', 'content', 'message_type']
    can_edit = True


class MessageAttachmentView(ModelView):
    datamodel = SQLAInterface(MessageAttachment)
    list_columns = ['id', 'message_id', 'file_url', 'file_type', 'uploaded_at']
    show_columns = ['id', 'message_id', 'file_url', 'file_type', 'uploaded_at']
    search_columns = ['file_type']
    edit_columns = ['message_id', 'file_url', 'file_type']
    add_columns = ['message_id', 'file_url', 'file_type']


# Users are managed through Flask-AppBuilder's built-in User management

appbuilder.add_view(
    ChatRoomView,
    "聊天室",
    icon="fa-comment",
    category="聊天室管理"
)

appbuilder.add_view(
    RoomMemberView,
    "聊天室成員",
    icon="fa-user-plus",
    category="聊天室管理"
)

appbuilder.add_view(
    MessageView,
    "訊息",
    icon="fa-envelope",
    category="聊天室管理"
)

appbuilder.add_view(
    MessageAttachmentView,
    "訊息附件",
    icon="fa-paperclip",
    category="聊天室管理"
)

# 為數據管理添加私訊和用戶狀態的 ModelView
class PrivateMessageDataView(ModelView):
    datamodel = SQLAInterface(PrivateMessage)
    list_columns = ['id', 'sender_id', 'receiver_id', 'content', 'message_type', 'is_read', 'created_at']
    show_columns = ['id', 'sender_id', 'receiver_id', 'content', 'message_type', 'is_read', 'created_at']
    search_columns = ['content', 'message_type']
    edit_columns = ['sender_id', 'receiver_id', 'content', 'message_type', 'is_read']
    add_columns = ['sender_id', 'receiver_id', 'content', 'message_type']

class UserStatusDataView(ModelView):
    datamodel = SQLAInterface(UserStatus)
    list_columns = ['id', 'user_id', 'status', 'last_seen', 'status_message']
    show_columns = ['id', 'user_id', 'status', 'last_seen', 'status_message']
    search_columns = ['status', 'status_message']
    

appbuilder.add_view(
    PrivateMessageDataView,
    "私人訊息",
    icon="fa-envelope-o",
    category="聊天室管理"
)

appbuilder.add_view(
    UserStatusDataView,
    "用戶狀態",
    icon="fa-circle",
    category="聊天室管理"
)


# Using Flask-AppBuilder's built-in User API instead


class ChatRoomApi(ModelRestApi):
    datamodel = SQLAInterface(ChatRoom)
    resource_name = 'rooms'


class RoomMemberApi(ModelRestApi):
    datamodel = SQLAInterface(RoomMember)
    resource_name = 'members'


class MessageApi(ModelRestApi):
    datamodel = SQLAInterface(Message)
    resource_name = 'messages'


class MessageAttachmentApi(ModelRestApi):
    datamodel = SQLAInterface(MessageAttachment)
    resource_name = 'attachments'




class PrivateMessageApi(ModelRestApi):
    datamodel = SQLAInterface(PrivateMessage)
    resource_name = 'private_messages'


class UserStatusApi(ModelRestApi):
    datamodel = SQLAInterface(UserStatus)
    resource_name = 'user_status'


# Flask-AppBuilder provides built-in User API
appbuilder.add_api(ChatRoomApi)
appbuilder.add_api(RoomMemberApi)
appbuilder.add_api(MessageApi)
appbuilder.add_api(MessageAttachmentApi)
appbuilder.add_api(PrivateMessageApi)
appbuilder.add_api(UserStatusApi)

# Using Flask-AppBuilder's built-in authentication instead
appbuilder.add_view_no_menu(ChatRoomManageView())
appbuilder.add_view_no_menu(MessageManageView())
appbuilder.add_view_no_menu(PrivateMessageManageView())
appbuilder.add_view_no_menu(UserStatusManageView())
appbuilder.add_view_no_menu(AdminView())

# 用户注册 API
appbuilder.add_api(RegisterApi)



"""
    Application wide 404 error handler
"""


@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        404,
    )

db.create_all()
