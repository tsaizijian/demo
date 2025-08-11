"""
自訂認證 API - 產生 JWT token
"""

from flask import request, jsonify, current_app
from flask_appbuilder.api import BaseApi
from flask_appbuilder import expose
from flask_appbuilder.security.decorators import protect
import datetime
from werkzeug.security import check_password_hash

from .auth import create_jwt_token

class JWTAuthApi(BaseApi):
    """
    JWT 認證相關 API
    """
    
    resource_name = 'auth'
    
    @expose('/login', methods=['POST'])
    def login(self):
        """
        使用者登入，回傳 JWT token
        POST /api/v1/security/login
        """
        try:
            data = request.get_json()
            
            if not data or 'username' not in data or 'password' not in data:
                return jsonify({'message': '請提供使用者名稱和密碼'}), 400
            
            username = data['username']
            password = data['password']
            
            # 尋找使用者
            user = self.appbuilder.sm.find_user(username=username)
            
            if not user:
                return jsonify({'message': '使用者不存在'}), 401
            
            # 驗證密碼
            if not check_password_hash(user.password, password):
                return jsonify({'message': '密碼錯誤'}), 401
            
            # 檢查使用者是否啟用
            if not user.is_active:
                return jsonify({'message': '使用者帳號已停用'}), 401
            
            # 創建 JWT token
            access_token = create_jwt_token(user, current_app)
            
            # 回傳認證資訊
            return jsonify({
                'access_token': access_token,
                'token_type': 'Bearer',
                'expires_in': 7 * 24 * 60 * 60,  # 7 天（秒）
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'is_active': user.is_active
                }
            }), 200
            
        except Exception as e:
            current_app.logger.error(f"登入錯誤: {str(e)}")
            return jsonify({'message': '登入失敗'}), 500
    
    @expose('/me')
    @protect()
    def me(self):
        """
        取得當前使用者資訊
        GET /api/v1/security/me
        """
        try:
            from flask import g
            
            if not hasattr(g, 'user') or not g.user:
                return jsonify({'message': '未認證'}), 401
            
            user = g.user
            
            return jsonify({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'is_active': user.is_active
                }
            }), 200
            
        except Exception as e:
            current_app.logger.error(f"取得使用者資訊錯誤: {str(e)}")
            return jsonify({'message': '取得使用者資訊失敗'}), 500

class RegisterApi(BaseApi):
    """
    註冊相關 API
    """
    
    resource_name = 'register'
    
    @expose('/signup', methods=['POST'])
    def signup(self):
        """
        使用者註冊
        POST /api/v1/register/signup
        """
        try:
            data = request.get_json()
            
            required_fields = ['username', 'first_name', 'last_name', 'email', 'password']
            for field in required_fields:
                if not data or field not in data:
                    return jsonify({'message': f'缺少必要欄位: {field}'}), 400
            
            # 檢查使用者是否已存在
            if self.appbuilder.sm.find_user(username=data['username']):
                return jsonify({'message': '使用者名稱已存在'}), 400
                
            if self.appbuilder.sm.find_user(email=data['email']):
                return jsonify({'message': '電子郵件已註冊'}), 400
            
            # 建立新使用者
            role = self.appbuilder.sm.find_role('Public')  # 預設角色
            if not role:
                # 如果沒有 Public 角色，使用第一個可用角色
                role = self.appbuilder.sm.get_all_roles()[0]
            
            user = self.appbuilder.sm.add_user(
                username=data['username'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                role=role,
                password=data['password']
            )
            
            if user:
                return jsonify({
                    'success': True,
                    'message': '註冊成功',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email
                    }
                }), 201
            else:
                return jsonify({'message': '註冊失敗'}), 500
                
        except Exception as e:
            current_app.logger.error(f"註冊錯誤: {str(e)}")
            return jsonify({'message': '註冊失敗'}), 500
    
    @expose('/check-username', methods=['POST'])
    def check_username(self):
        """
        檢查使用者名稱是否可用
        POST /api/v1/register/check-username
        """
        try:
            data = request.get_json()
            
            if not data or 'username' not in data:
                return jsonify({'message': '請提供使用者名稱'}), 400
            
            username = data['username']
            user = self.appbuilder.sm.find_user(username=username)
            
            return jsonify({
                'available': user is None
            }), 200
            
        except Exception as e:
            current_app.logger.error(f"檢查使用者名稱錯誤: {str(e)}")
            return jsonify({'message': '檢查失敗'}), 500