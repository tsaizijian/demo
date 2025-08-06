from flask import request, jsonify, current_app
from flask_appbuilder.api import BaseApi, expose

import re

class RegisterApi(BaseApi):
    """
    使用者註冊 API
    """
    resource_name = "register"
    
    @expose('/signup', methods=['POST'])
    def signup(self):
        """
        使用者註冊端點
        """
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '請提供註冊資料'
                }), 400
            
            # 驗證必填欄位
            required_fields = ['username', 'first_name', 'last_name', 'email', 'password']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({
                        'success': False,
                        'message': f'{field} 為必填欄位'
                    }), 400
            
            username = data.get('username').strip()
            first_name = data.get('first_name').strip()
            last_name = data.get('last_name').strip()
            email = data.get('email').strip()
            password = data.get('password')
            
            # 驗證格式
            if len(username) < 3:
                return jsonify({
                    'success': False,
                    'message': '使用者名稱至少需要3個字元'
                }), 400
            
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                return jsonify({
                    'success': False,
                    'message': '使用者名稱只能包含字母、數字和底線'
                }), 400
            
            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                return jsonify({
                    'success': False,
                    'message': '請輸入有效的電子郵件格式'
                }), 400
            
            if len(password) < 6:
                return jsonify({
                    'success': False,
                    'message': '密碼至少需要6個字元'
                }), 400
            
            # 使用全局的appbuilder實例  
            from app import appbuilder
            
            # 檢查使用者名稱是否已存在
            existing_user = appbuilder.sm.find_user(username=username)
            if existing_user:
                return jsonify({
                    'success': False,
                    'message': '此使用者名稱已被使用'
                }), 400
            
            # 檢查電子郵件是否已存在
            existing_email = appbuilder.sm.find_user(email=email)
            if existing_email:
                return jsonify({
                    'success': False,
                    'message': '此電子郵件已被註冊'
                }), 400
            
            # 創建新使用者
            try:
                # 取得預設的使用者角色
                public_role = appbuilder.sm.find_role(appbuilder.sm.auth_user_registration_role)
                if not public_role:
                    public_role = appbuilder.sm.find_role('Public')
                
                # 新增使用者
                new_user = appbuilder.sm.add_user(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    role=public_role,
                    password=password
                )
                
                if new_user:
                    return jsonify({
                        'success': True,
                        'message': '註冊成功！',
                        'user': {
                            'id': new_user.id,
                            'username': new_user.username,
                            'first_name': new_user.first_name,
                            'last_name': new_user.last_name,
                            'email': new_user.email
                        }
                    }), 201
                else:
                    return jsonify({
                        'success': False,
                        'message': '註冊失敗，請稍後再試'
                    }), 500
                    
            except Exception as e:
                current_app.logger.error(f'註冊用戶失敗: {e}')
                return jsonify({
                    'success': False,
                    'message': '註冊失敗，請稍後再試'
                }), 500
                
        except Exception as e:
            current_app.logger.error(f'註冊API錯誤: {e}')
            return jsonify({
                'success': False,
                'message': '伺服器錯誤'
            }), 500
    
    @expose('/check-username', methods=['POST'])
    def check_username(self):
        """
        檢查使用者名稱是否可用
        """
        try:
            data = request.get_json()
            username = data.get('username', '').strip()
            
            if not username:
                return jsonify({
                    'available': False,
                    'message': '請提供使用者名稱'
                }), 400
            
            from app import appbuilder
            existing_user = appbuilder.sm.find_user(username=username)
            
            return jsonify({
                'available': existing_user is None,
                'message': '使用者名稱已被使用' if existing_user else '使用者名稱可以使用'
            })
            
        except Exception as e:
            current_app.logger.error(f'檢查使用者名稱錯誤: {e}')
            return jsonify({
                'available': False,
                'message': '檢查失敗'
            }), 500