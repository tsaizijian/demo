import os
from dotenv import load_dotenv
from flask_appbuilder.security.manager import (
    AUTH_OID,
    AUTH_REMOTE_USER,
    AUTH_DB,
    AUTH_LDAP,
    AUTH_OAUTH,
)

load_dotenv(override=True)
basedir = os.path.abspath(os.path.dirname(__file__))


FAB_API_SWAGGER_UI = True
# Your App secret key
SECRET_KEY = os.getenv("SECRET_KEY")

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS = False
# print(f"Using database URI: {SQLALCHEMY_DATABASE_URI}")

# SQLALCHEMY_DATABASE_URI = 'mysql://myapp@localhost/myapp'
# SQLALCHEMY_DATABASE_URI = 'postgresql://root:password@localhost/myapp'

# Flask-WTF flag for CSRF
CSRF_ENABLED = True

# RECAPTCHA Configuration (臨時禁用用於測試)
RECAPTCHA_PUBLIC_KEY = ""  # 空值會禁用 reCAPTCHA
RECAPTCHA_PRIVATE_KEY = ""  # 空值會禁用 reCAPTCHA


# ----------------------------------------------------
# AUTHENTICATION CONFIG
# ----------------------------------------------------
# The authentication type
# AUTH_OID : Is for OpenID
# AUTH_DB : Is for database (username/password()
# AUTH_LDAP : Is for LDAP
# AUTH_REMOTE_USER : Is for using REMOTE_USER from web server

# Uncomment to setup Full admin role name
# AUTH_ROLE_ADMIN = 'Admin'

# Uncomment to setup Public role name, no authentication needed
# AUTH_ROLE_PUBLIC = 'Public'

# Will allow user self registration
AUTH_USER_REGISTRATION = True

# The default user self registration role
AUTH_USER_REGISTRATION_ROLE = "Public"



AUTH_TYPE = AUTH_DB

OAUTH_PROVIDERS = [
    {
        'name': 'google',
        'icon': 'fa-google',
        'token_key': 'access_token',
        'remote_app': {
            'client_id': os.getenv("GOOGLE_CLIENT_ID"),
            'client_secret': os.getenv("GOOGLE_CLIENT_SECRET"),
            'api_base_url': 'https://www.googleapis.com/oauth2/v2/',
            'client_kwargs': {
                'scope': 'email profile'
            },
            'request_token_url': None,
            'access_token_url': 'https://oauth2.googleapis.com/token',
            'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        }
    }
]


BABEL_DEFAULT_LOCALE = "en"
AUTH_USER_REGISTRATION = False


# Your application default translation path
BABEL_DEFAULT_FOLDER = "translations"
# The allowed translation for you app
LANGUAGES = {
    "en": {"flag": "gb", "name": "English"},
    "pt": {"flag": "pt", "name": "Portuguese"},
    "pt_BR": {"flag": "br", "name": "Pt Brazil"},
    "es": {"flag": "es", "name": "Spanish"},
    "de": {"flag": "de", "name": "German"},
    "zh": {"flag": "cn", "name": "Chinese"},
    "ru": {"flag": "ru", "name": "Russian"},
    "pl": {"flag": "pl", "name": "Polish"},
}
# ---------------------------------------------------
# Image and file configuration
# ---------------------------------------------------
# The file upload folder, when using models with files
UPLOAD_FOLDER = basedir + "/app/static/uploads/"

# The image upload folder, when using models with images
IMG_UPLOAD_FOLDER = basedir + "/app/static/uploads/"

# The image upload url, when using models with images
IMG_UPLOAD_URL = "/static/uploads/"
# Setup image size default is (300, 200, True)
# IMG_SIZE = (300, 200, True)

