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

# 啟用 CORS
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

db = SQLA(app)
# 使用自訂的 JWT 安全管理器
appbuilder = AppBuilder(app, db.session, security_manager_class=JWTSecurityManager)


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
