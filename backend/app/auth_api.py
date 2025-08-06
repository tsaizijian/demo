from flask import request, jsonify
from flask_appbuilder.api import BaseApi, expose
from flask_appbuilder.security.decorators import protect
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash
from .base_views import ChatBaseView
from . import appbuilder


class AuthApi(BaseApi):
    """
    認證相關 API
    """
    
    route_base = '/api/auth'
    
    @expose('/login', methods=['POST'])
    def login(self):
        """
        用戶登入 API
        ---
        post:
          description: 用戶登入
          requestBody:
            required: true
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    username:
                      type: string
                      description: 用戶名或郵箱
                    password:
                      type: string
                      description: 密碼
                  required:
                    - username
                    - password
          responses:
            200:
              description: 登入成功
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      success:
                        type: boolean
                      message:
                        type: string
                      user:
                        type: object
                        properties:
                          id:
                            type: integer
                          username:
                            type: string
                          first_name:
                            type: string
                          last_name:
                            type: string
                          email:
                            type: string
            400:
              description: 請求參數錯誤
            401:
              description: 認證失敗
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': '請提供登入資訊'
                }), 400
            
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return jsonify({
                    'success': False,
                    'message': '用戶名和密碼不能為空'
                }), 400
            
            # 使用 Flask-AppBuilder 的用戶查找功能
            user = None
            
            # 嘗試以用戶名查找
            user = appbuilder.sm.find_user(username=username)
            
            # 如果沒找到，嘗試以郵箱查找
            if not user and '@' in username:
                user = appbuilder.sm.find_user(email=username)
            
            if not user:
                return jsonify({
                    'success': False,
                    'message': '用戶不存在'
                }), 401
            
            # 檢查密碼
            if not check_password_hash(user.password, password):
                return jsonify({
                    'success': False,
                    'message': '密碼錯誤'
                }), 401
            
            # 檢查用戶是否啟用
            if not user.active:
                return jsonify({
                    'success': False,
                    'message': '用戶帳戶已被停用'
                }), 401
            
            # 登入用戶
            login_user(user)
            
            return jsonify({
                'success': True,
                'message': '登入成功',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                    'email': user.email or ''
                }
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'登入過程中發生錯誤: {str(e)}'
            }), 500
    
    @expose('/logout', methods=['POST'])
    def logout(self):
        """
        用戶登出 API
        ---
        post:
          description: 用戶登出
          responses:
            200:
              description: 登出成功
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      success:
                        type: boolean
                      message:
                        type: string
        """
        try:
            logout_user()
            return jsonify({
                'success': True,
                'message': '登出成功'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'登出過程中發生錯誤: {str(e)}'
            }), 500
    
    @expose('/me', methods=['GET'])
    @protect()
    def me(self):
        """
        獲取當前用戶資訊 API
        ---
        get:
          description: 獲取當前登入用戶的資訊
          responses:
            200:
              description: 成功獲取用戶資訊
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      success:
                        type: boolean
                      user:
                        type: object
                        properties:
                          id:
                            type: integer
                          username:
                            type: string
                          first_name:
                            type: string
                          last_name:
                            type: string
                          email:
                            type: string
                          roles:
                            type: array
                            items:
                              type: string
            401:
              description: 未登入
        """
        try:
            if not current_user or not current_user.is_authenticated:
                return jsonify({
                    'success': False,
                    'message': '用戶未登入'
                }), 401
            
            user_roles = [role.name for role in current_user.roles] if current_user.roles else []
            
            return jsonify({
                'success': True,
                'user': {
                    'id': current_user.id,
                    'username': current_user.username,
                    'first_name': current_user.first_name or '',
                    'last_name': current_user.last_name or '',
                    'email': current_user.email or '',
                    'roles': user_roles
                }
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'獲取用戶資訊時發生錯誤: {str(e)}'
            }), 500

    @expose('/check', methods=['GET'])
    def check_auth(self):
        """
        檢查認證狀態 API
        ---
        get:
          description: 檢查用戶是否已登入
          responses:
            200:
              description: 認證狀態
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      authenticated:
                        type: boolean
                      user_id:
                        type: integer
                        nullable: true
        """
        try:
            if current_user and current_user.is_authenticated:
                return jsonify({
                    'authenticated': True,
                    'user_id': current_user.id
                })
            else:
                return jsonify({
                    'authenticated': False,
                    'user_id': None
                })
        except Exception as e:
            return jsonify({
                'authenticated': False,
                'user_id': None,
                'error': str(e)
            })