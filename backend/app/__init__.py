import logging

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA
from flask_cors import CORS

# 匯入自訂的安全管理器
from .auth import JWTSecurityManager

"""
 Logging configuration
"""

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)

app.config.from_object("config")

db = SQLA(app)

appbuilder = AppBuilder(app, db.session, security_manager_class=JWTSecurityManager)

CORS(
    app,
    resources=r"/api/*",                          # 只針對 /api/ 路徑
    origins=["http://localhost:3000"],            # 前端固定的來源
    supports_credentials=True,                    # 讓 Cookie/Session 可跨域
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],   # 允許 JWT header
    expose_headers=["Content-Type", "Authorization"],
)

# 使用自訂的 JWT 安全管理器


"""
from sqlalchemy.engine import Engine
from sqlalchemy import event

#Only include this for SQLLite constraints
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # Will force sqllite contraint foreign keys
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
"""

from . import views, socketio_server

# 🔄 初始化資料庫 Hook
from .hooks import setup_database_hooks
setup_database_hooks()
