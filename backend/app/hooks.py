"""
資料庫 Hook 系統
處理成員數量同步和密碼加密等自動化任務
"""
from sqlalchemy import event, text
try:
    from flask_bcrypt import Bcrypt
    # 初始化 bcrypt
    bcrypt = Bcrypt()
    HAS_BCRYPT = True
except ImportError:
    print("⚠️ Flask-Bcrypt not installed, password hashing disabled")
    HAS_BCRYPT = False
    bcrypt = None


def setup_database_hooks():
    """設置所有資料庫 Hook"""
    from .models import ChannelMember, ChatChannel
    
    # 🔄 成員變更時自動更新數量
    @event.listens_for(ChannelMember, 'after_insert')
    @event.listens_for(ChannelMember, 'after_update') 
    @event.listens_for(ChannelMember, 'after_delete')
    def update_channel_member_count(mapper, connection, target):
        """成員變更時自動更新頻道成員數量"""
        if hasattr(target, 'channel_id'):
            # 使用原始 SQL 避免 ORM 會話問題
            count_query = text("""
                SELECT COUNT(*) FROM channel_members 
                WHERE channel_id = :channel_id AND status = 'active'
            """)
            result = connection.execute(
                count_query, 
                {'channel_id': target.channel_id}
            ).scalar()
            
            # 更新頻道成員數量
            update_query = text("""
                UPDATE chat_channels 
                SET member_count = :count, changed_on = datetime('now')
                WHERE id = :channel_id
            """)
            connection.execute(
                update_query, 
                {'count': result, 'channel_id': target.channel_id}
            )

    # 密碼加密 Hook
    if HAS_BCRYPT:
        @event.listens_for(ChatChannel.join_password, 'set', retval=True)
        def hash_password(target, value, oldvalue, initiator):
            """密碼設定時自動加密"""
            if value and value != oldvalue:
                return bcrypt.generate_password_hash(value).decode('utf-8')
            return value

    print("✅ Database hooks initialized")