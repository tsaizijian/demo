from flask import request, jsonify, current_app
from flask_appbuilder.api import BaseApi, expose
from flask_appbuilder.security.sqla.models import Role
from werkzeug.security import generate_password_hash
import re
import requests
from . import db
from .models import MyUser
from flask import make_response
import os
from dotenv import load_dotenv
load_dotenv(override=True)


RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_SECRET_KEY")

def verify_recaptcha(token: str) -> bool:
    secret = current_app.config.get("RECAPTCHA_SECRET")
    response = requests.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={"secret": secret, "response": token}
    )
    result = response.json()
    return result.get("success", False) and result.get("score", 0) >= 0.5


class RegisterApi(BaseApi):
    """
    用戶註冊 API
    """
    route_base = '/api/register'
    @expose("", methods=["OPTIONS", "POST"])
    def options(self):
        """
        處理 CORS 預檢請求
        """
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.status_code = 200
        return response
    
  
    @expose('/user', methods=['POST'])
    def register_user(self):
        """
        用戶註冊 API
        
        POST /api/register/user
        {
            "username": "testuser",
            "email": "test@example.com", 
            "first_name": "Test",
            "last_name": "User",
            "password": "password123",
            "recaptcha_response": "03AGdBq25..."
        }
        """
        try:
            data = request.get_json()
            
            # ✅ 統一使用 recaptcha_response
            token = data.get("recaptcha_response")

            if not token:
                return self.response_400(message="reCAPTCHA token 缺失")

            # ✅ 進行 Google 驗證
            secret = os.getenv("APP_RECAPTCHA_SECRET")
            verify_res = requests.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data={"secret": secret, "response": token}
            )
            result = verify_res.json()
            print("🔐 reCAPTCHA 結果：", result)

            if not result.get("success") or result.get("score", 0) < 0.5:
                return self.response_400(message="reCAPTCHA 驗證失敗")

            # ✅ 檢查必要欄位（此時已驗證成功）
            required_fields = ['username', 'email', 'first_name', 'last_name', 'password']
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                return jsonify({
                    'success': False,
                    'message': f'缺少必要字段: {", ".join(missing_fields)}'
                }), 400
            
            username = data['username'].strip()
            email = data['email'].strip()
            first_name = data['first_name'].strip()
            last_name = data['last_name'].strip()
            password = data['password']
            
            # 驗證用戶名格式
            if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
                return jsonify({
                    'success': False,
                    'message': '用戶名必須為3-20個字符，只能包含字母、數字和下劃線'
                }), 400
            
            # 驗證郵箱格式
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return jsonify({
                    'success': False,
                    'message': '郵箱格式不正確'
                }), 400
            
            # 驗證密碼強度
            if len(password) < 6:
                return jsonify({
                    'success': False,
                    'message': '密碼至少需要6個字符'
                }), 400
            
            # 檢查用戶名是否已存在
            existing_user = db.session.query(MyUser).filter_by(username=username).first()
            if existing_user:
                return jsonify({
                    'success': False,
                    'message': '用戶名已存在'
                }), 409
            
            # 檢查郵箱是否已存在
            existing_email = db.session.query(MyUser).filter_by(email=email).first()
            if existing_email:
                return jsonify({
                    'success': False,
                    'message': '郵箱已被註冊'
                }), 409
            
            # 獲取或創建 Public 角色
            public_role = db.session.query(Role).filter_by(name='Public').first()
            if not public_role:
                public_role = Role(name='Public')
                db.session.add(public_role)
                db.session.commit()
            
            # 創建新用戶
            new_user = MyUser(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=generate_password_hash(password),
                active=True
            )
            
            # 添加角色
            new_user.roles.append(public_role)
            
            # 保存到數據庫
            db.session.add(new_user)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': '用戶註冊成功',
                'data': {
                    'user_id': new_user.id,
                    'username': new_user.username,
                    'email': new_user.email,
                    'first_name': new_user.first_name,
                    'last_name': new_user.last_name,
                }
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'註冊失敗: {str(e)}'
            }), 500
    
    @expose('/check-username', methods=['POST'])
    def check_username(self):
        """
        檢查用戶名是否可用
        
        POST /api/register/check-username
        {
            "username": "testuser"
        }
        """
        try:
            data = request.get_json()
            username = data.get('username', '').strip()
            
            if not username:
                return jsonify({
                    'success': False,
                    'message': '用戶名不能為空'
                }), 400
            
            # 驗證用戶名格式
            if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
                return jsonify({
                    'success': False,
                    'available': False,
                    'message': '用戶名必須為3-20個字符，只能包含字母、數字和下劃線'
                }), 200
            
            # 檢查是否已存在
            existing_user = db.session.query(MyUser).filter_by(username=username).first()
            available = existing_user is None
            
            return jsonify({
                'success': True,
                'available': available,
                'message': '用戶名可用' if available else '用戶名已存在'
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'檢查失敗: {str(e)}'
            }), 500
    
    @expose('/check-email', methods=['POST'])
    def check_email(self):
        """
        檢查郵箱是否可用
        
        POST /api/register/check-email
        {
            "email": "test@example.com"
        }
        """
        try:
            data = request.get_json()
            email = data.get('email', '').strip()
            
            if not email:
                return jsonify({
                    'success': False,
                    'message': '郵箱不能為空'
                }), 400
            
            # 驗證郵箱格式
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return jsonify({
                    'success': False,
                    'available': False,
                    'message': '郵箱格式不正確'
                }), 200
            
            # 檢查是否已存在
            existing_email = db.session.query(MyUser).filter_by(email=email).first()
            available = existing_email is None
            
            return jsonify({
                'success': True,
                'available': available,
                'message': '郵箱可用' if available else '郵箱已被註冊'
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'檢查失敗: {str(e)}'
            }), 500
    