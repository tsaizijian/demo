from flask import request, session
from functools import wraps
import json
import os

class I18n:
    def __init__(self, app=None):
        self.app = app
        self.translations = {}
        self.default_language = 'zh'
        self.supported_languages = ['zh', 'en', 'ja', 'ko']
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        self.load_translations()
        
        @app.before_request
        def set_language():
            # 從 URL 參數、會話或請求頭獲取語言設置
            lang = request.args.get('lang') or \
                   session.get('language') or \
                   request.headers.get('Accept-Language', '').split(',')[0][:2] or \
                   self.default_language
            
            if lang not in self.supported_languages:
                lang = self.default_language
            
            session['language'] = lang
            request.language = lang
    
    def load_translations(self):
        """載入翻譯文件"""
        translations_dir = os.path.join(os.path.dirname(__file__), 'translations')
        
        for lang in self.supported_languages:
            lang_file = os.path.join(translations_dir, f'{lang}.json')
            if os.path.exists(lang_file):
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations[lang] = json.load(f)
            else:
                self.translations[lang] = {}
    
    def get_text(self, key, lang=None):
        """獲取翻譯文本"""
        if lang is None:
            lang = getattr(request, 'language', self.default_language)
        
        return self.translations.get(lang, {}).get(key, key)
    
    def t(self, key, lang=None):
        """翻譯函數的簡寫"""
        return self.get_text(key, lang)

# 全局翻譯實例
i18n = I18n()

def _(key):
    """全局翻譯函數"""
    return i18n.get_text(key)

def get_current_language():
    """獲取當前語言"""
    return getattr(request, 'language', i18n.default_language)

def localized_response(func):
    """裝飾器：本地化 API 響應"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        
        # 如果返回的是 tuple (response, status_code)
        if isinstance(result, tuple) and len(result) == 2:
            response_data, status_code = result
            if isinstance(response_data, dict) and 'message' in response_data:
                response_data['message'] = _(response_data['message'])
            if isinstance(response_data, dict) and 'error' in response_data:
                response_data['error'] = _(response_data['error'])
            return response_data, status_code
        
        return result
    return wrapper