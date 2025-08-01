import logging
from flask import Flask
from flask_appbuilder import AppBuilder, SQLA


"""
 Logging configuration
"""
logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)

app.config.from_object("config")

# Ensure that JSON responses are not escaped
app.json.ensure_ascii = False 



db = SQLA(app)

appbuilder = AppBuilder(
    app,
    db.session,
)

from . import views