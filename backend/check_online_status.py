#!/usr/bin/env python3
"""
檢查資料庫中的線上使用者狀態
"""
import sys
import os

# 添加專案根目錄到路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from app.models import UserProfile

def check_online_users():
    """檢查線上使用者狀態"""
    with app.app_context():
        print("=== 資料庫中的線上使用者狀態 ===")
        
        # 查詢所有使用者
        all_users = db.session.query(UserProfile).all()
        print(f"總使用者數: {len(all_users)}")
        
        # 查詢線上使用者
        online_users = db.session.query(UserProfile).filter_by(is_online=True).all()
        print(f"線上使用者數: {len(online_users)}")
        
        print("\n=== 所有使用者詳細資訊 ===")
        for user in all_users:
            status = "🟢 線上" if user.is_online else "🔴 離線"
            print(f"ID: {user.id} | User ID: {user.user_id} | {user.display_name} | {status} | 最後上線: {user.last_seen}")
        
        if online_users:
            print("\n=== 目前線上使用者 ===")
            for user in online_users:
                print(f"- {user.display_name} (ID: {user.user_id})")
        else:
            print("\n✅ 沒有使用者處於線上狀態")

if __name__ == "__main__":
    check_online_users()