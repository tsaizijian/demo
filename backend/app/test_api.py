from flask import jsonify
from flask_appbuilder.api import BaseApi, expose
from flask_appbuilder.security.decorators import protect
from flask_login import current_user
from . import appbuilder


class TestApi(BaseApi):
    """
    測試 API - 用於驗證 CORS 和認證
    """
    
    route_base = '/api/test'
    
    @expose('/public', methods=['GET', 'OPTIONS'])
    def public_test(self):
        """
        公開測試端點（不需要認證）
        """
        return jsonify({
            'success': True,
            'message': '公開端點測試成功',
            'cors_working': True
        })
    
    @expose('/auth', methods=['GET', 'OPTIONS'])
    @protect()
    def auth_test(self):
        """
        認證測試端點（需要認證）
        """
        return jsonify({
            'success': True,
            'message': '認證端點測試成功',
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email
            } if current_user and current_user.is_authenticated else None,
            'authenticated': current_user.is_authenticated if current_user else False
        })