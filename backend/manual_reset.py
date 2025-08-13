#!/usr/bin/env python3
"""
手動重置線上狀態
"""
import sys
import os
import sqlite3

# 直接操作 SQLite 資料庫
db_path = '/home/jian/Desktop/chatroom_v2/backend/app.db'

def reset_online_status():
    """直接使用 SQL 重置線上狀態"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查看當前線上使用者
        cursor.execute("SELECT id, user_id, display_name, is_online FROM user_profiles")
        users = cursor.fetchall()
        
        print("=== 重置前的狀態 ===")
        for user in users:
            status = "🟢 線上" if user[3] else "🔴 離線"
            print(f"ID: {user[0]} | User ID: {user[1]} | Name: {user[2]} | {status}")
        
        online_count = sum(1 for user in users if user[3])
        print(f"線上使用者數: {online_count}")
        
        # 直接更新 SQL
        cursor.execute("""
            UPDATE user_profiles 
            SET is_online = 0, 
                changed_on = datetime('now'),
                changed_by_fk = user_id
            WHERE is_online = 1
        """)
        
        updated_count = cursor.rowcount
        conn.commit()
        
        print(f"\n✅ 成功重置 {updated_count} 個使用者的線上狀態")
        
        # 再次檢查
        cursor.execute("SELECT id, user_id, display_name, is_online FROM user_profiles")
        users = cursor.fetchall()
        
        print("\n=== 重置後的狀態 ===")
        for user in users:
            status = "🟢 線上" if user[3] else "🔴 離線"
            print(f"ID: {user[0]} | User ID: {user[1]} | Name: {user[2]} | {status}")
        
        online_count = sum(1 for user in users if user[3])
        print(f"線上使用者數: {online_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 重置失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reset_online_status()