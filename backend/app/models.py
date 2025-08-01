from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from flask_appbuilder.security.sqla.models import User
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from . import db

# 自定義 User 模型繼承 Flask-AppBuilder 的 User
class MyUser(User):
    __tablename__ = 'ab_user'

    
    def __repr__(self):
        return f'<MyUser {self.username}>'


class ChatRoom(Model, AuditMixin):
    __tablename__ = 'chat_rooms'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_private = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey('ab_user.id'), nullable=False)
    
    # Relationships
    members = relationship('RoomMember', backref='room', lazy='dynamic')
    messages = relationship('Message', backref='room', lazy='dynamic')

    @property
    def member_count(self):
        return self.members.count()
    def __repr__(self):
        return f'<ChatRoom {self.name}>'
    


class RoomMember(Model, AuditMixin):
    __tablename__ = 'room_members'
    
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('chat_rooms.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('ab_user.id'), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    is_admin = Column(Boolean, default=False)

    def __repr__(self):
        return f'<RoomMember room_id={self.room_id} user_id={self.user_id}>'


class Message(Model, AuditMixin):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('chat_rooms.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('ab_user.id'), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default='text')  # text, image, file
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    attachments = relationship('MessageAttachment', backref='message', lazy='dynamic')

    def __repr__(self):
        return f'<Message {self.id} from user {self.user_id}>'


class MessageAttachment(Model, AuditMixin):
    __tablename__ = 'message_attachments'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('messages.id'), nullable=False)
    file_url = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)

    def __repr__(self):
        return f'<MessageAttachment {self.id} for message {self.message_id}>'


class PrivateMessage(Model, AuditMixin):
    __tablename__ = 'private_messages'
    
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('ab_user.id'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('ab_user.id'), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default='text')  # text, image, file
    is_read = Column(Boolean, default=False)
    is_deleted_by_sender = Column(Boolean, default=False)
    is_deleted_by_receiver = Column(Boolean, default=False)
    
    # Relationships
    sender = relationship('User', foreign_keys=[sender_id], backref='sent_private_messages')
    receiver = relationship('User', foreign_keys=[receiver_id], backref='received_private_messages')

    def __repr__(self):
        return f'<PrivateMessage {self.id} from {self.sender_id} to {self.receiver_id}>'


class UserStatus(Model, AuditMixin):
    __tablename__ = 'user_status'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('ab_user.id'), nullable=False, unique=True)
    status = Column(String(20), default='offline')  # online, offline, away, busy
    last_seen = Column(DateTime, default=datetime.utcnow)
    status_message = Column(String(255), nullable=True)
    
    # Relationships
    user = relationship('User', foreign_keys=[user_id], backref='status')

    def __repr__(self):
        return f'<UserStatus {self.user_id}: {self.status}>'
