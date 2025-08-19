#!/usr/bin/env python3
"""
頻道成員管理功能資料庫遷移腳本
創建新的資料表並初始化現有頻道的擁有者記錄
"""
import os
import sys
from datetime import datetime, timezone

# 添加 app 目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA
from app.auth import JWTSecurityManager
from app.models import ChatChannel, ChannelMember
from sqlalchemy import text


def create_app():
    """創建 Flask 應用程式"""
    app = Flask(__name__)
    app.config.from_object("config")
    
    # 不載入 hooks 避免循環引用
    return app


def main():
    """執行遷移"""
    print("🚀 開始頻道成員管理功能資料庫遷移...")
    
    app = create_app()
    db = SQLA(app)
    appbuilder = AppBuilder(app, db.session, security_manager_class=JWTSecurityManager)
    
    with app.app_context():
        try:
            # 1. 創建新資料表
            print("📋 創建 channel_members 資料表...")
            db.create_all()
            
            # 2. 檢查 ChatChannel 是否需要新增欄位
            print("🔧 檢查 chat_channels 資料表結構...")
            
            # 檢查新欄位是否存在
            result = db.session.execute(text("PRAGMA table_info(chat_channels)")).fetchall()
            existing_columns = [row[1] for row in result]
            
            new_columns = [
                'member_count',
                'join_password', 
                'password_required',
                'allow_join_by_id'
            ]
            
            for column in new_columns:
                if column not in existing_columns:
                    if column == 'member_count':
                        print(f"➕ 添加欄位: {column}")
                        db.session.execute(text(f"ALTER TABLE chat_channels ADD COLUMN {column} INTEGER DEFAULT 0"))
                    elif column == 'join_password':
                        print(f"➕ 添加欄位: {column}")
                        db.session.execute(text(f"ALTER TABLE chat_channels ADD COLUMN {column} VARCHAR(255)"))
                    elif column in ['password_required', 'allow_join_by_id']:
                        print(f"➕ 添加欄位: {column}")
                        db.session.execute(text(f"ALTER TABLE chat_channels ADD COLUMN {column} BOOLEAN DEFAULT 0"))
                else:
                    print(f"✅ 欄位已存在: {column}")
            
            # 3. 為現有頻道創建擁有者記錄
            print("👑 為現有頻道創建擁有者記錄...")
            
            # 獲取所有現有頻道
            channels = db.session.query(ChatChannel).all()
            created_count = 0
            
            with db.session.no_autoflush:
                for channel in channels:
                    # 檢查是否已有擁有者記錄
                    existing_owner = db.session.query(ChannelMember).filter_by(
                        channel_id=channel.id,
                        user_id=channel.creator_id,
                        role='owner'
                    ).first()
                    
                    if not existing_owner:
                        # 創建擁有者記錄
                        owner_member = ChannelMember(
                            channel_id=channel.id,
                            user_id=channel.creator_id,
                            role='owner',
                            status='active',
                            created_on=channel.created_on or datetime.now(timezone.utc),
                            changed_on=datetime.now(timezone.utc),
                            created_by_fk=channel.creator_id,
                            changed_by_fk=channel.creator_id
                        )
                        db.session.add(owner_member)
                        created_count += 1
                        print(f"  📝 創建頻道 '{channel.name}' 的擁有者記錄 (user_id: {channel.creator_id})")
                
                # 手動 flush 來保存記錄，但不觸發 Hook
                db.session.flush()
            
            # 4. 初始化所有頻道的成員數量
            print("🔢 初始化頻道成員數量...")
            
            update_sql = text("""
                UPDATE chat_channels 
                SET member_count = (
                    SELECT COUNT(*) FROM channel_members 
                    WHERE channel_members.channel_id = chat_channels.id 
                    AND channel_members.status = 'active'
                )
            """)
            
            result = db.session.execute(update_sql)
            db.session.commit()
            
            print(f"✅ 成功創建 {created_count} 個擁有者記錄")
            print(f"✅ 更新了所有頻道的成員數量")
            print("🎉 資料庫遷移完成!")
            
        except Exception as e:
            print(f"❌ 遷移失敗: {str(e)}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)