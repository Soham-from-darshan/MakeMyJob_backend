from datetime import timedelta
import string
import json
from cryptography.fernet import Fernet

with open('./instance/email_cred.json','r') as f:
    email_creds = json.load(f)
    

class FlaskDefaultConfiguration:
    DEBUG = False
    TESTING = False
    PROPAGATE_EXCEPTIONS = None
    TRAP_HTTP_EXCEPTIONS = False
    TRAP_BAD_REQUEST_ERRORS = None
    SECRET_KEY = None
    SESSION_COOKIE_NAME = 'session'
    SESSION_COOKIE_DOMAIN = None
    SESSION_COOKIE_PATH = None
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = None
    PERMANENT_SESSION_LIFETIME = timedelta(days=31)
    SESSION_REFRESH_EACH_REQUEST = True
    USE_X_SENDFILE = False
    SEND_FILE_MAX_AGE_DEFAULT = None
    SERVER_NAME = None
    APPLICATION_ROOT = '/'
    PREFERRED_URL_SCHEME = 'http'
    MAX_CONTENT_LENGTH = None
    TEMPLATES_AUTO_RELOAD = None
    EXPLAIN_TEMPLATE_LOADING = False
    MAX_COOKIE_SIZE = 4093


class DefaultConfiguration(FlaskDefaultConfiguration):
    SECRET_KEY = 'fake secret'                           # type: ignore

    MIN_USERNAME_LENGTH = 2
    MAX_USERNAME_LENGTH = 20
    USERNAME_CAN_CONTAIN = string.ascii_letters + " "
    OTP_EXPIRY_IN_MINUTES = 10.0
    ENABLE_SCHEDULER = True
    INACTIVE_ACCOUNT_DELETION_INTERVAL_IN_HOURS = 1.0
    ACCEPTABLE_INACTIVITY_IN_YEARS = 1

    MAIL_USERNAME = email_creds['address']
    MAIL_DEFAULT_SENDER = email_creds['address']
    MAIL_PASSWORD = email_creds['password']
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    JWT_ERROR_MESSAGE_KEY = 'description'

    SEND_OTP = 'send_otp'
    CIPHER = Fernet(Fernet.generate_key())



class DevelopmentConfiguration(DefaultConfiguration):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///debug.db'
    SQLALCHEMY_ECHO=True


class TestingConfiguration(DefaultConfiguration):
    TESTING = True
    PROPAGATE_EXCEPTIONS = False                 # type: ignore

    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    MAIL_SUPPRESS_SEND = True

    OTP_EXPIRY_IN_MINUTES = .2/6
    SEND_OTP = 'send_otp_for_test'
    INACTIVE_ACCOUNT_DELETION_INTERVAL_IN_HOURS = 2/3600

    

class DeploymentConfiguration(DefaultConfiguration):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///production.db'


