#!/usr/bin/env python3
"""
初始化預設資料腳本
建立預設頻道和必要的初始資料
"""

import sys
import os

# 添加專案路徑
sys.path.append('/home/jian/Desktop/chatroom_v2/backend')

from app import db, appbuilder
from app.models import ChatChannel

def create_default_channels():
    """建立預設頻道"""
    print("=== 檢查並建立預設頻道 ===")
    
    # 檢查現有頻道
    existing_channels = db.session.query(ChatChannel).all()
    print(f"現有頻道數量: {len(existing_channels)}")
    
    for channel in existing_channels:
        print(f"- {channel.id}: {channel.name} (私人: {channel.is_private})")
    
    # 如果沒有頻道，建立預設頻道
    if len(existing_channels) == 0:
        print("\n建立預設頻道...")
        
        # 尋找管理員使用者
        admin_user = appbuilder.sm.find_user(username='admin')
        if not admin_user:
            # 如果沒有admin，使用第一個使用者
            all_users = appbuilder.sm.get_all_users()
            if all_users:
                admin_user = all_users[0]
                print(f"使用 {admin_user.username} 作為頻道建立者")
            else:
                print("錯誤: 找不到任何使用者，無法建立預設頻道")
                return False
        
        # 建立預設頻道
        default_channels = [
            {
                'name': 'general',
                'description': '一般討論頻道，歡迎大家在這裡聊天',
                'is_private': False,
                'max_members': 1000
            },
            {
                'name': 'random',
                'description': '隨意聊天的頻道',
                'is_private': False,
                'max_members': 500
            },
            {
                'name': 'announcements',
                'description': '重要公告頻道',
                'is_private': False,
                'max_members': 1000
            }
        ]
        
        created_channels = []
        
        for channel_data in default_channels:
            try:
                channel = ChatChannel(
                    name=channel_data['name'],
                    description=channel_data['description'],
                    is_private=channel_data['is_private'],
                    is_active=True,
                    creator_id=admin_user.id,
                    max_members=channel_data['max_members']
                )
                
                db.session.add(channel)
                created_channels.append(channel)
                
            except Exception as e:
                print(f"建立頻道 {channel_data['name']} 時發生錯誤: {e}")
                db.session.rollback()
                return False
        
        # 提交所有變更
        try:
            db.session.commit()
            print(f"\n✅ 成功建立 {len(created_channels)} 個預設頻道:")
            for channel in created_channels:
                print(f"   - {channel.name} (ID: {channel.id})")
            return True
            
        except Exception as e:
            print(f"❌ 提交資料庫時發生錯誤: {e}")
            db.session.rollback()
            return False
    
    else:
        print("✅ 已存在頻道，無需建立預設頻道")
        return True

def check_permissions():
    """檢查權限設定"""
    print("\n=== 檢查權限設定 ===")
    
    # 檢查是否存在Public角色
    public_role = appbuilder.sm.find_role('Public')
    if public_role:
        print(f"✅ 找到Public角色: {public_role.name}")
        
        # 檢查角色權限
        permissions = public_role.permissions
        channel_permissions = [p for p in permissions if 'chatchannel' in p.permission.name.lower()]
        
        print(f"   頻道相關權限數量: {len(channel_permissions)}")
        for perm in channel_permissions:
            print(f"   - {perm.permission.name} on {perm.view_menu.name}")
    
    else:
        print("❌ 找不到Public角色")

def main():
    """主函式"""
    print("🚀 初始化聊天室預設資料")
    print("=" * 50)
    
    try:
        # 建立預設頻道
        success = create_default_channels()
        if not success:
            print("❌ 初始化失敗")
            sys.exit(1)
        
        # 檢查權限
        check_permissions()
        
        print("\n" + "=" * 50)
        print("✅ 初始化完成!")
        
    except Exception as e:
        print(f"❌ 初始化過程中發生錯誤: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()