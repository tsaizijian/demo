from flask import render_template
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, ModelRestApi

from . import appbuilder, db
from .models import ChatMessage, UserProfile, ChatChannel
from .apis import ChatMessageApi, UserProfileApi, ChatChannelApi

# Register REST APIs
appbuilder.add_api(ChatMessageApi)
appbuilder.add_api(UserProfileApi)
appbuilder.add_api(ChatChannelApi)

# Import and register security APIs
from .security_apis import JWTAuthApi, RegisterApi
appbuilder.add_api(JWTAuthApi)
appbuilder.add_api(RegisterApi)


# Create Model Views for Admin Interface
class ChatMessageView(ModelView):
    """聊天訊息管理介面"""
    datamodel = SQLAInterface(ChatMessage)
    
    list_columns = ['id', 'content', 'message_type', 'created_on', 'is_deleted']
    show_columns = ['id', 'content', 'message_type', 'attachment_path', 'channel_id', 'is_deleted', 'created_on', 'changed_on']
    search_columns = ['content', 'message_type']
    
    base_order = ('created_on', 'desc')
    base_permissions = ['can_list', 'can_show', 'can_delete']


class UserProfileView(ModelView):
    """使用者資料管理介面"""
    datamodel = SQLAInterface(UserProfile)
    
    list_columns = ['id', 'display_name', 'is_online', 'join_date', 'last_seen']
    show_columns = ['id', 'display_name', 'avatar_url', 'bio', 'is_online', 'join_date', 'last_seen', 'timezone', 'language']
    search_columns = ['display_name']
    
    base_order = ('join_date', 'desc')


class ChatChannelView(ModelView):
    """聊天頻道管理介面"""
    datamodel = SQLAInterface(ChatChannel)
    
    list_columns = ['id', 'name', 'description', 'is_private', 'is_active', 'created_on']
    show_columns = ['id', 'name', 'description', 'is_private', 'is_active', 'max_members', 'created_on', 'changed_on']
    add_columns = ['name', 'description', 'is_private', 'max_members']
    edit_columns = ['name', 'description', 'is_private', 'is_active', 'max_members']
    search_columns = ['name', 'description']
    
    base_order = ('created_on', 'desc')


# Register Admin Views
appbuilder.add_view(
    ChatMessageView,
    "聊天訊息",
    icon="fa-comments",
    category="聊天室管理",
    category_icon='fa-comment'
)

appbuilder.add_view(
    UserProfileView,
    "使用者資料",
    icon="fa-users",
    category="聊天室管理"
)

appbuilder.add_view(
    ChatChannelView,
    "聊天頻道",
    icon="fa-list-alt",
    category="聊天室管理"
)

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
