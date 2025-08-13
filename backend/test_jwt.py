#!/usr/bin/env python3
"""
簡單的 JWT 認證測試腳本
"""
import jwt
import datetime
from datetime import timezone
from app import app, appbuilder

def test_jwt_token():
    """測試 JWT token 創建和解碼"""
    
    # 創建測試 payload
    payload = {
        'user_id': 1,
        'username': 'jerry',
        'email': 'b30430624@gmail.com',
        'iat': datetime.datetime.now(timezone.utc),
        'exp': datetime.datetime.now(timezone.utc) + datetime.timedelta(days=7)
    }
    
    # 創建 JWT token
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    print(f"創建的 JWT token: {token}")
    
    # 嘗試解碼
    try:
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        print(f"解碼成功: {decoded}")
        
        # 測試找使用者
        user = appbuilder.sm.get_user_by_id(1)
        if user:
            print(f"找到使用者: id={user.id}, username={user.username}, active={user.is_active}")
        else:
            print("找不到使用者 ID 1")
            
    except Exception as e:
        print(f"JWT 解碼失敗: {e}")

if __name__ == "__main__":
    with app.app_context():
        test_jwt_token()