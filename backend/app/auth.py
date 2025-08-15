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
        print("🔧 初始化 JWTSecurityManager")
        super(JWTSecurityManager, self).__init__(appbuilder)
        # 註冊 JWT 認證的 before_request
        self.appbuilder.app.before_request(self.jwt_auth_handler)
        print("🔧 JWTSecurityManager 初始化完成")
    
    def has_access(self, permission_name, view_name):
        """
        重寫 has_access 方法，加入 JWT token 認證並正確檢查權限
        """
        print(f"has_access 被調用: {permission_name} on {view_name}")
        
        # 先嘗試 JWT 認證
        current_user = None
        if self.jwt_authenticate_user():
            current_user = g.user
            print(f"has_access: JWT 認證成功 user_id={current_user.id}")
        elif (hasattr(g, 'user') and g.user and 
              g.user.__class__.__name__ != 'AnonymousUserMixin' and 
              hasattr(g.user, 'id')):
            current_user = g.user
            print(f"has_access: 使用已存在的認證用戶 {g.user.id}")
        
        # 如果沒有認證用戶，對於 API 端點返回 False，對於其他端點使用預設行為
        if not current_user:
            api_view_names = [
                'ChatMessageApi', 'UserProfileApi', 'ChatChannelApi', 'JWTAuthApi', 'RegisterApi'
            ]
            if view_name in api_view_names:
                print(f"has_access: API 端點未認證 {view_name}.{permission_name}: False")
                return False
            else:
                print(f"has_access: 非 API 端點未認證，使用原有機制")
                return super(JWTSecurityManager, self).has_access(permission_name, view_name)
        
        # 🔒 區分管理界面權限和 API 端點權限
        admin_view_names = [
            'ChatMessageView', 'UserProfileView', 'ChatChannelView', 'UserView',
            'UserDBModelView', 'RoleModelView', 'PermissionModelView', 'ViewMenuModelView',
            'PermissionViewModelView', 'UserGroupModelView', 'RegisterUserModelView'
        ]
        
        api_view_names = [
            'ChatMessageApi', 'UserProfileApi', 'ChatChannelApi', 'JWTAuthApi', 'RegisterApi'
        ]
        
        # 管理界面的權限檢查
        if view_name in admin_view_names:
            is_admin = (hasattr(current_user, 'roles') and 
                       any(role.name == 'Admin' for role in current_user.roles))
            print(f"has_access: 管理界面權限檢查 {view_name}.{permission_name} for user {current_user.id}: {is_admin}")
            return is_admin
        
        # API 端點權限檢查 - 認證用戶都可以存取
        if view_name in api_view_names:
            print(f"has_access: API 端點權限 {view_name}.{permission_name} for user {current_user.id}: True")
            return True
        
        # 對於其他權限，使用預設行為
        print(f"has_access: 未定義權限類型 {view_name}.{permission_name} for user {current_user.id}: 使用預設")
        return super(JWTSecurityManager, self).has_access(permission_name, view_name)
    
    def check_authorization(self, perms=None, dag_id=None):
        """Override check_authorization if it exists"""
        print(f"🔍 check_authorization 被調用: perms={perms}, dag_id={dag_id}")
        return super().check_authorization(perms, dag_id) if hasattr(super(), 'check_authorization') else True
    
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
                        # 同時設定 Flask-Login 的 current_user
                        from flask_login import login_user
                        login_user(user, remember=False)
                        print(f"JWT 認證成功: user_id={user.id}, username={user.username}, 已設置 current_user")
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
                        # 設定 Flask-Login 的 current_user
                        from flask_login import login_user
                        login_user(user, remember=False)
                        print(f"JWT 認證成功: user_id={user.id}, username={user.username}, 已設置 current_user")
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