"""
JWT Bearer Token Authentication for Flask-AppBuilder
處理 JWT token 認證並設定 g.user
"""

import jwt
from flask import request, g, current_app
from flask_appbuilder.security.sqla.manager import SecurityManager
from flask_login import current_user
from functools import wraps
import datetime
from datetime import timezone

class JWTSecurityManager(SecurityManager):
    """
    自訂的安全管理器，支援 JWT Bearer token 認證
    """
    
    def __init__(self, appbuilder):
        super(JWTSecurityManager, self).__init__(appbuilder)
        # 註冊 JWT 認證的 before_request
        self.appbuilder.app.before_request(self.jwt_auth_handler)
    
    def has_access(self, permission_name, view_name):
        """
        重寫 has_access 方法，加入 JWT token 認證並正確檢查權限
        """
        # 檢查是否為匿名使用者，如果是，嘗試 JWT 認證
        current_user = None
        if (hasattr(g, 'user') and g.user and 
            g.user.__class__.__name__ != 'AnonymousUserMixin' and 
            hasattr(g.user, 'id')):
            current_user = g.user
            print(f"has_access: 已認證使用者 {g.user.id}")
        elif self.jwt_authenticate_user():
            current_user = g.user
            print(f"has_access: JWT 認證成功")
        else:
            print(f"has_access: 無法認證，使用原有機制")
            # 回退到原有的認證機制
            return super(JWTSecurityManager, self).has_access(permission_name, view_name)
        
        # 🔒 對於管理相關的權限，檢查用戶是否為管理員
        admin_permissions = [
            'can_list', 'can_show', 'can_add', 'can_edit', 'can_delete',
            'menu_access'  # 菜單存取權限
        ]
        
        if permission_name in admin_permissions:
            # 檢查是否為管理員
            is_admin = (hasattr(current_user, 'roles') and 
                       any(role.name == 'Admin' for role in current_user.roles))
            print(f"has_access: 管理權限檢查 {permission_name} for user {current_user.id}: {is_admin}")
            return is_admin
        
        # 對於非管理權限，認證用戶都可以存取（如 API 端點）
        return True
    
    def jwt_authenticate_user(self):
        """
        JWT 使用者認證，如果成功設定 g.user 並返回 True
        """
        # 檢查 Authorization header
        auth_header = request.headers.get('Authorization')
        print(f"JWT 認證嘗試: {auth_header[:50] if auth_header else 'No header'}...")
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            try:
                # 解碼 JWT token
                payload = jwt.decode(
                    token, 
                    current_app.config['SECRET_KEY'], 
                    algorithms=['HS256']
                )
                
                # 檢查 token 是否過期
                if 'exp' in payload:
                    exp_timestamp = payload['exp']
                    if datetime.datetime.now(timezone.utc).timestamp() > exp_timestamp:
                        print("JWT Token 已過期")
                        return False
                
                # 根據 token 中的 user_id 找到使用者
                user_id = payload.get('user_id')
                if user_id:
                    user = self.get_user_by_id(user_id)
                    if user and user.is_active:
                        g.user = user
                        print(f"JWT 認證成功: user_id={user.id}, username={user.username}")
                        return True
                    else:
                        print(f"使用者不存在或未啟用: user_id={user_id}")
                        return False
                else:
                    print("JWT payload 中沒有 user_id")
                    return False
                    
            except jwt.ExpiredSignatureError:
                print("JWT Token 已過期")
                return False
            except jwt.InvalidTokenError as e:
                print(f"JWT Token 無效: {str(e)}")
                return False
            except Exception as e:
                print(f"JWT 認證錯誤: {str(e)}")
                return False
        
        return False
    
    def jwt_auth_handler(self):
        """
        在每個請求前檢查 JWT token
        如果有效，設定 g.user
        """
        print(f"JWT 中間件被調用: {request.method} {request.path}")
        
        # 跳過靜態文件和 /api/v1/security/login 等認證端點
        if (request.endpoint and 
            (request.endpoint.startswith('static') or 
             request.path.startswith('/static') or
             request.path == '/api/v1/security/login' or
             request.path == '/api/v1/auth/login' or
             request.path.startswith('/api/v1/register/'))):
            print(f"跳過認證端點: {request.path}")
            return
        
        # 檢查 Authorization header
        auth_header = request.headers.get('Authorization')
        print(f"Authorization header: {auth_header[:50] if auth_header else 'None'}...")
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            try:
                # 解碼 JWT token
                payload = jwt.decode(
                    token, 
                    current_app.config['SECRET_KEY'], 
                    algorithms=['HS256']
                )
                
                # 檢查 token 是否過期
                if 'exp' in payload:
                    exp_timestamp = payload['exp']
                    if datetime.datetime.now(timezone.utc).timestamp() > exp_timestamp:
                        g.user = None
                        return
                
                # 根據 token 中的 user_id 找到使用者
                user_id = payload.get('user_id')
                if user_id:
                    # 使用正確的參數名稱查詢使用者
                    user = self.get_user_by_id(user_id)
                    if user and user.is_active:
                        g.user = user
                        print(f"JWT 認證成功: user_id={user.id}, username={user.username}")
                        # 也設定 flask-login 的 current_user（如果需要）
                        # login_user(user)
                    else:
                        print(f"使用者不存在或未啟用: user_id={user_id}")
                        g.user = None
                else:
                    print("JWT payload 中沒有 user_id")
                    g.user = None
                    
            except jwt.ExpiredSignatureError:
                print("JWT Token 已過期")
                g.user = None
            except jwt.InvalidTokenError as e:
                print(f"JWT Token 無效: {str(e)}")
                g.user = None
            except Exception as e:
                print(f"JWT 認證錯誤: {str(e)}")
                g.user = None
        else:
            # 沒有 Authorization header，檢查是否有 session 認證
            if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
                g.user = current_user
            else:
                g.user = None

def jwt_required(f):
    """
    裝飾器：要求有效的 JWT token
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'user') or not g.user:
            from flask import jsonify
            return jsonify({'error': '需要認證'}), 401
        return f(*args, **kwargs)
    return decorated_function

def create_jwt_token(user, app):
    """
    為使用者創建 JWT token
    """
    payload = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'iat': datetime.datetime.now(timezone.utc),
        'exp': datetime.datetime.now(timezone.utc) + datetime.timedelta(days=7)  # 7 天過期
    }
    
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

def verify_jwt_token(token, app):
    """
    驗證 JWT token
    """
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None