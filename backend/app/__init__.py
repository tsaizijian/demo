import logging
from flask import Flask
from flask_appbuilder import AppBuilder, SQLA
from flask_cors import CORS

# Logging
logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_object("config")

# JSON 中文不轉義
app.config['JSON_AS_ASCII'] = False

# Session 配置，支持跨域
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # 在開發環境使用 Lax
app.config['SESSION_COOKIE_SECURE'] = False  # 在開發環境設為 False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_DOMAIN'] = None  # 允許 localhost

# 強化 CORS 設定 - 允許所有聊天相關路由
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept"],
        "supports_credentials": True,
    }
})

# 資料庫
db = SQLA(app)

# AppBuilder 啟用
appbuilder = AppBuilder(app, db.session)

from . import views
