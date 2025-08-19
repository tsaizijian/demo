#!/usr/bin/env python3
"""
設定API權限腳本
為Public角色添加頻道管理相關權限
"""

import sys
import os

# 添加專案路徑
sys.path.append('/home/jian/Desktop/chatroom_v2/backend')

from app import db, appbuilder

def setup_channel_permissions():
    """為所有相關角色設定頻道相關權限"""
    print("=== 設定頻道API權限 ===")
    
    # 取得所有可能的角色
    roles_to_update = []
    
    # 嘗試取得Public角色
    public_role = appbuilder.sm.find_role('Public')
    if public_role:
        roles_to_update.append(public_role)
        print(f"✅ 找到Public角色: {public_role.name}")
    
    # 嘗試取得User角色
    user_role = appbuilder.sm.find_role('User')
    if user_role:
        roles_to_update.append(user_role)
        print(f"✅ 找到User角色: {user_role.name}")
    
    # 如果沒有找到任何角色，列出所有可用的角色
    if not roles_to_update:
        all_roles = appbuilder.sm.get_all_roles()
        print("❌ 找不到Public或User角色，所有可用角色:")
        for role in all_roles:
            print(f"  - {role.name}")
            if role.name in ['Public', 'User', 'Gamma']:
                roles_to_update.append(role)
    
    if not roles_to_update:
        print("❌ 找不到任何適當的角色來設定權限")
        return False
    
    # ChatChannelApi 權限
    channel_permissions = [
        'can_get_public_channels',
        'can_create_channel', 
        'can_get_my_channels',
        'can_get',
        'can_post',
        'can_put',
        'can_edit',
        'can_delete'
    ]
    
    # ChannelMemberApi 權限
    member_permissions = [
        'can_get_channel_members',
        'can_join_channel_by_id', 
        'can_leave_channel',
        'can_remove_member',
        'can_transfer_ownership',
        'can_update_member_role',
        'can_reset_channel_password',
        'can_get_channel_admin_info',
        'can_post',  # 允許 POST 請求
        'can_put',   # 允許 PUT 請求  
        'can_get'    # 允許 GET 請求
    ]
    
    # 設定 ChatChannelApi 權限
    channel_view_menu = appbuilder.sm.find_view_menu('ChatChannelApi')
    if not channel_view_menu:
        print("❌ 找不到ChatChannelApi視圖選單")
        return False
    print(f"✅ 找到視圖選單: {channel_view_menu.name}")
    
    # 設定 ChannelMemberApi 權限
    member_view_menu = appbuilder.sm.find_view_menu('ChannelMemberApi')
    if not member_view_menu:
        print("❌ 找不到ChannelMemberApi視圖選單")
        return False
    print(f"✅ 找到視圖選單: {member_view_menu.name}")
    
    # 為每個權限建立PermissionView並添加到所有目標角色
    added_permissions = []
    
    # 處理 ChatChannelApi 權限
    for perm_name in channel_permissions:
        try:
            permission = appbuilder.sm.find_permission(perm_name)
            if not permission:
                permission = appbuilder.sm.add_permission(perm_name)
                print(f"   建立新權限: {perm_name}")
            
            perm_view = appbuilder.sm.find_permission_view_menu(perm_name, channel_view_menu.name)
            if not perm_view:
                perm_view = appbuilder.sm.add_permission_view_menu(perm_name, channel_view_menu.name)
                print(f"   建立權限視圖: {perm_name} on {channel_view_menu.name}")
            
            for role in roles_to_update:
                if perm_view not in role.permissions:
                    role.permissions.append(perm_view)
                    added_permissions.append(f"{perm_name} -> {role.name}")
                    print(f"   ✅ 添加權限到{role.name}角色: {perm_name}")
                else:
                    print(f"   ⭕ {role.name}角色已有權限: {perm_name}")
        except Exception as e:
            print(f"   ❌ 處理權限 {perm_name} 時發生錯誤: {e}")
    
    # 處理 ChannelMemberApi 權限
    for perm_name in member_permissions:
        try:
            permission = appbuilder.sm.find_permission(perm_name)
            if not permission:
                permission = appbuilder.sm.add_permission(perm_name)
                print(f"   建立新權限: {perm_name}")
            
            perm_view = appbuilder.sm.find_permission_view_menu(perm_name, member_view_menu.name)
            if not perm_view:
                perm_view = appbuilder.sm.add_permission_view_menu(perm_name, member_view_menu.name)
                print(f"   建立權限視圖: {perm_name} on {member_view_menu.name}")
            
            for role in roles_to_update:
                if perm_view not in role.permissions:
                    role.permissions.append(perm_view)
                    added_permissions.append(f"{perm_name} -> {role.name}")
                    print(f"   ✅ 添加權限到{role.name}角色: {perm_name}")
                else:
                    print(f"   ⭕ {role.name}角色已有權限: {perm_name}")
        except Exception as e:
            print(f"   ❌ 處理權限 {perm_name} 時發生錯誤: {e}")
    
    # 提交變更
    try:
        db.session.commit()
        print(f"\n✅ 成功添加 {len(added_permissions)} 個權限到Public角色")
        return True
    except Exception as e:
        print(f"❌ 提交權限變更時發生錯誤: {e}")
        db.session.rollback()
        return False

def check_current_permissions():
    """檢查當前權限狀況"""
    print("\n=== 檢查當前權限狀況 ===")
    
    public_role = appbuilder.sm.find_role('Public')
    if not public_role:
        print("❌ 找不到Public角色")
        return
    
    # 顯示所有權限
    all_permissions = public_role.permissions
    channel_permissions = [p for p in all_permissions if 'chatchannel' in p.view_menu.name.lower()]
    
    print(f"Public角色總權限數: {len(all_permissions)}")
    print(f"頻道相關權限數: {len(channel_permissions)}")
    
    if channel_permissions:
        print("頻道相關權限列表:")
        for perm in channel_permissions:
            print(f"  - {perm.permission.name} on {perm.view_menu.name}")
    else:
        print("❌ 沒有頻道相關權限")

def main():
    """主函式"""
    print("🔐 設定聊天室API權限")
    print("=" * 50)
    
    try:
        # 檢查當前權限
        check_current_permissions()
        
        # 設定權限
        success = setup_channel_permissions()
        if not success:
            print("❌ 權限設定失敗")
            sys.exit(1)
        
        # 再次檢查權限
        check_current_permissions()
        
        print("\n" + "=" * 50)
        print("✅ 權限設定完成!")
        print("請重新啟動後端伺服器以套用變更")
        
    except Exception as e:
        print(f"❌ 權限設定過程中發生錯誤: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()