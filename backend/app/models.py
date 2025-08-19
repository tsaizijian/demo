from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from flask_appbuilder.security.sqla.models import User
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Index, JSON
from sqlalchemy.orm import relationship
import datetime
from .time_utils import to_iso_utc


class ChatMessage(AuditMixin, Model):
    """
    聊天室訊息模型
    繼承 AuditMixin 自動追蹤 created_on, changed_on, created_by, changed_by
    """
    __tablename__ = 'chat_messages'

    # 主鍵
    id = Column(Integer, primary_key=True)

    # 訊息內容
    content = Column(Text, nullable=False, comment='訊息內容')

    # 發送者資訊 (關聯到 Flask-AppBuilder 的 User 模型)
    sender_id = Column(Integer, ForeignKey('ab_user.id'), nullable=False)
    sender = relationship("User", foreign_keys=[sender_id], backref="chat_messages")

    # 訊息類型 (text, image, file, system)
    message_type = Column(String(20), default='text', comment='訊息類型')

    # 附件路徑 (如果有上傳檔案)
    attachment_path = Column(String(255), nullable=True, comment='附件路徑')

    # 是否已刪除 (軟刪除)
    is_deleted = Column(Boolean, default=False, comment='是否已刪除')

    # 回覆訊息 ID (支援回覆功能)
    reply_to_id = Column(Integer, ForeignKey('chat_messages.id'), nullable=True)
    reply_to = relationship("ChatMessage", remote_side=[id], backref="replies")

    # 頻道/房間 ID (未來擴充多房間功能)
    channel_id = Column(Integer, default=1, comment='頻道ID')

    # 資料庫索引優化
    __table_args__ = (
        # 依建立時間排序的索引 (最常用的查詢)
        Index('idx_chat_messages_created_on', 'created_on'),
        # 依發送者查詢的索引
        Index('idx_chat_messages_sender_id', 'sender_id'),
        # 依頻道查詢的索引
        Index('idx_chat_messages_channel_id', 'channel_id'),
        # 複合索引：頻道 + 建立時間
        Index('idx_chat_messages_channel_created', 'channel_id', 'created_on'),
    )

    def __repr__(self):
        return f'<ChatMessage {self.id}: {self.content[:50]}>'

    def to_dict(self):
        """轉換為字典格式，供 API 回傳使用"""
        try:
            sender_name = 'Unknown'
            sender_first_name = ''
            sender_last_name = ''
            
            if self.sender:
                sender_name = getattr(self.sender, 'username', 'Unknown')
                sender_first_name = getattr(self.sender, 'first_name', '')
                sender_last_name = getattr(self.sender, 'last_name', '')
            
            return {
                'id': self.id,
                'content': self.content,
                'sender_id': self.sender_id,
                'sender_name': sender_name,
                'sender_first_name': sender_first_name,
                'sender_last_name': sender_last_name,
                'message_type': self.message_type,
                'attachment_path': self.attachment_path,
                'is_deleted': self.is_deleted,
                'reply_to_id': self.reply_to_id,
                'channel_id': self.channel_id,
                'created_on': to_iso_utc(self.created_on),
                'changed_on': to_iso_utc(self.changed_on)
            }
        except Exception as e:
            # 如果出現任何錯誤，返回基本資訊
            return {
                'id': getattr(self, 'id', None),
                'content': getattr(self, 'content', ''),
                'sender_id': getattr(self, 'sender_id', None),
                'sender_name': 'Unknown',
                'sender_first_name': '',
                'sender_last_name': '',
                'message_type': getattr(self, 'message_type', 'text'),
                'attachment_path': getattr(self, 'attachment_path', None),
                'is_deleted': getattr(self, 'is_deleted', False),
                'reply_to_id': getattr(self, 'reply_to_id', None),
                'channel_id': getattr(self, 'channel_id', 1),
                'created_on': None,
                'changed_on': None
            }


class ChannelMember(AuditMixin, Model):
    """頻道成員關係模型"""
    __tablename__ = 'channel_members'

    id = Column(Integer, primary_key=True)

    # 關聯關係
    channel_id = Column(Integer, ForeignKey('chat_channels.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('ab_user.id'), nullable=False)

    # 關聯對象
    channel = relationship("ChatChannel", backref="members")
    user = relationship("User", foreign_keys=[user_id], backref="channel_memberships")

    # 成員角色
    role = Column(String(20), default='member', comment='成員角色: owner, admin, member')

    # 加入狀態
    status = Column(String(20), default='active', comment='成員狀態: active, invited, banned, left')

    # 索引優化
    __table_args__ = (
        # 確保同一用戶在同一頻道只有一個有效記錄
        Index('idx_channel_user_unique', 'channel_id', 'user_id'),
        Index('idx_channel_members_status', 'channel_id', 'status'),
        Index('idx_user_channels', 'user_id', 'status'),
    )

    def __repr__(self):
        return f'<ChannelMember {self.user_id}@{self.channel_id} ({self.role})>'

    def to_dict(self):
        """轉換為字典格式，供 API 回傳使用"""
        try:
            username = ''
            display_name = ''
            if self.user:
                username = getattr(self.user, 'username', '')
                # 嘗試獲取 display_name（可能來自 UserProfile）
                if hasattr(self.user, 'profile') and self.user.profile:
                    display_name = getattr(self.user.profile, 'display_name', username)
                else:
                    display_name = f"{getattr(self.user, 'first_name', '')} {getattr(self.user, 'last_name', '')}".strip() or username
            
            return {
                'id': self.id,
                'channel_id': self.channel_id,
                'user_id': self.user_id,
                'username': username,
                'display_name': display_name,
                'role': self.role,
                'status': self.status,
                'created_on': to_iso_utc(self.created_on),
                'changed_on': to_iso_utc(self.changed_on)
            }
        except Exception as e:
            return {
                'id': getattr(self, 'id', None),
                'channel_id': getattr(self, 'channel_id', None),
                'user_id': getattr(self, 'user_id', None),
                'username': '',
                'display_name': '',
                'role': getattr(self, 'role', 'member'),
                'status': getattr(self, 'status', 'active'),
                'created_on': None,
                'changed_on': None
            }


class UserProfile(AuditMixin, Model):
    """
    使用者資料擴充模型 (擴充 Flask-AppBuilder User)
    """
    __tablename__ = 'user_profiles'

    # 主鍵
    id = Column(Integer, primary_key=True)

    # 關聯到 Flask-AppBuilder 的 User 模型
    user_id = Column(Integer, ForeignKey('ab_user.id'), nullable=False, unique=True)
    user = relationship("User", foreign_keys=[user_id], backref="profile")

    # 聊天室顯示名稱
    display_name = Column(String(50), nullable=True, comment='聊天室顯示名稱')

    # 大頭貼網址
    avatar_url = Column(String(255), nullable=True, comment='大頭貼網址')

    # 個人簡介
    bio = Column(Text, nullable=True, comment='個人簡介')

    # 是否線上
    is_online = Column(Boolean, default=False, comment='是否線上')

    # 最後上線時間
    last_seen = Column(DateTime, nullable=True, comment='最後上線時間')

    # 發送訊息總數
    message_count = Column(Integer, default=0, comment='發送訊息總數')

    # 加入日期
    join_date = Column(DateTime, default=datetime.datetime.utcnow, comment='加入日期')

    # 時區設定
    timezone = Column(String(50), default='UTC', comment='時區設定')

    # 語言偏好
    language = Column(String(10), default='zh-TW', comment='語言偏好')

    # 通知設定 (JSON)
    notification_settings = Column(JSON, nullable=True, comment='通知設定')

    def __repr__(self):
        return f'<UserProfile {self.user.username if self.user else self.user_id}>'

    def to_dict(self):
        """轉換為字典格式，供 API 回傳使用"""
        try:
            username = ''
            if self.user:
                username = getattr(self.user, 'username', '')
            
            return {
                'id': self.id,
                'user_id': self.user_id,
                'username': username,
                'display_name': self.display_name or username,
                'avatar_url': self.avatar_url,
                'bio': self.bio,
                'is_online': self.is_online,
                'last_seen': self.last_seen.isoformat() if self.last_seen else None,
                'message_count': self.message_count,
                'join_date': self.join_date.isoformat() if self.join_date else None,
                'timezone': self.timezone,
                'language': self.language,
                'notification_settings': self.notification_settings
            }
        except Exception as e:
            return {
                'id': getattr(self, 'id', None),
                'user_id': getattr(self, 'user_id', None),
                'username': '',
                'display_name': getattr(self, 'display_name', ''),
                'avatar_url': getattr(self, 'avatar_url', None),
                'bio': getattr(self, 'bio', None),
                'is_online': getattr(self, 'is_online', False),
                'last_seen': None,
                'message_count': getattr(self, 'message_count', 0),
                'join_date': None,
                'timezone': getattr(self, 'timezone', 'UTC'),
                'language': getattr(self, 'language', 'zh-TW'),
                'notification_settings': getattr(self, 'notification_settings', None)
            }


class ChatChannel(AuditMixin, Model):
    """
    聊天頻道/房間模型 (未來擴充多房間功能)
    """
    __tablename__ = 'chat_channels'

    # 主鍵
    id = Column(Integer, primary_key=True)

    # 頻道名稱
    name = Column(String(100), nullable=False, comment='頻道名稱')

    # 頻道描述
    description = Column(Text, nullable=True, comment='頻道描述')

    # 是否為私人頻道
    is_private = Column(Boolean, default=False, comment='是否為私人頻道')

    # 是否啟用
    is_active = Column(Boolean, default=True, comment='是否啟用')

    # 頻道建立者
    creator_id = Column(Integer, ForeignKey('ab_user.id'), nullable=False)
    creator = relationship("User", foreign_keys=[creator_id], backref="created_channels")

    # 最大成員數
    max_members = Column(Integer, default=100, comment='最大成員數')
    
    # 🆕 新增欄位：成員數量 - 自動同步更新
    member_count = Column(Integer, default=0, comment='成員數量 - 自動同步更新')

    # 🆕 頻道密碼功能
    join_password = Column(String(255), nullable=True, comment='頻道加入密碼 (bcrypt 加密)')
    password_required = Column(Boolean, default=False, comment='是否需要密碼才能加入')
    allow_join_by_id = Column(Boolean, default=False, comment='是否允許通過頻道ID直接加入')

    def __repr__(self):
        return f'<ChatChannel {self.id}: {self.name}>'

    def to_dict(self):
        """轉換為字典格式，供 API 回傳使用"""
        try:
            creator_name = ''
            if self.creator:
                creator_name = getattr(self.creator, 'username', '')
            
            return {
                'id': self.id,
                'name': self.name,
                'description': self.description,
                'is_private': self.is_private,
                'is_active': self.is_active,
                'creator_id': self.creator_id,
                'creator_name': creator_name,
                'max_members': self.max_members,
                'member_count': self.member_count,
                'password_required': self.password_required,
                'allow_join_by_id': self.allow_join_by_id,
                'created_on': to_iso_utc(self.created_on)
            }
        except Exception as e:
            return {
                'id': getattr(self, 'id', None),
                'name': getattr(self, 'name', ''),
                'description': getattr(self, 'description', ''),
                'is_private': getattr(self, 'is_private', False),
                'is_active': getattr(self, 'is_active', True),
                'creator_id': getattr(self, 'creator_id', None),
                'creator_name': '',
                'max_members': getattr(self, 'max_members', 100),
                'member_count': getattr(self, 'member_count', 0),
                'password_required': getattr(self, 'password_required', False),
                'allow_join_by_id': getattr(self, 'allow_join_by_id', False),
                'created_on': None
            }
    
    def update_member_count(self):
        """更新成員數量"""
        from sqlalchemy import func
        from . import db
        self.member_count = db.session.query(func.count(ChannelMember.id))\
            .filter_by(channel_id=self.id, status='active').scalar()
        db.session.commit()

