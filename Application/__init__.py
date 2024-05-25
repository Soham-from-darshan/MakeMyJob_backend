from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import MappedAsDataclass, DeclarativeBase
from werkzeug import exceptions
from typing import cast
from enum import StrEnum
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from cryptography.fernet import Fernet
from base64 import b64encode
from instance import DefaultConfiguration

CurrentConfiguration = DefaultConfiguration

class Base(MappedAsDataclass, DeclarativeBase):
    def serialize(self) -> dict:
        table = self.__table__
        result = {}
        for col in table.columns:
            col_name = str(col).split('.')[-1]
            result[col_name] = getattr(self, col_name)
        # return json.dumps(result, default=str) # for stringification
        return result

    
db: SQLAlchemy = SQLAlchemy(model_class=Base)
jwt = JWTManager()
mail = Mail()
cipher = None


def create_app(*,configClass: type) -> Flask:
    """Create WSGI application instance, apply given configuration. Initialize extensions and create database from models then register blueprints and a generic error handler to jsonify any defalut errors. Return app instance.

    Args:
        config (type): A class that represents app configurations. This class is instantiated and passed to Flask.config.from_object method.

    Returns:
        Flask: The WSGI application instance.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(configClass())
    
    global CurrentConfiguration
    CurrentConfiguration = configClass

    import Application.errorhandlers as errhndl
    app.register_error_handler(exceptions.HTTPException, errhndl.jsonify_default_errors)
    app.register_error_handler(ValueError, errhndl.handle_value_error)
    app.register_error_handler(KeyError, errhndl.handle_key_error)

    mail.init_app(app)
    jwt.init_app(app)
    db.init_app(app)
    global cipher
    key = Fernet.generate_key()
    cipher = Fernet(key)


    import Application.models as models
    with app.app_context():
        db.create_all()    

    import Application.controllers.authentication as auth
    app.register_blueprint(auth.bp)
    
    @app.route('/')
    def home():
        return 'Hello world'
    
    # """These routes mimic the behaviour of unexpected errors. 
    # """
    # @app.route('/errorTest1')
    # def unknownErrorTestingRoute1():
    #     raise Exception('An Exception with single Argument')
    
    # @app.route('/errorTest2')
    # def unknownErrorTestingRoute2():
    #     raise Exception('An Exception','with','multiple','Arguments')
    
    return app


class EnumStore:
    """A class to logically group all enums used by application. Enums are stored directly in this class or stored in nested classes to keep everything organized.
    
    There are several benifits of using enums over hardcoding strings:
        - Change value at one place and it will reflect everywhere
        - Error is detected if there is mistake in spelling unlike hardcoded strings
        - The enums are logically grouped which means we can see natural patterns in code when its time extend features 
    """
    
    class HTTPMethod(StrEnum):
        GET = 'GET'
        POST = 'POST'
        PATCH = 'PATCH'
        DELETE = 'DELETE'
    
    class JSONSchema:
        """Collection of enums which represents json schema for api. 
        """
        class Error(StrEnum):
            NAME = 'name'
            CODE = 'code'
            DESCRIPTION = 'description'
        
        class User(StrEnum):
            NAME = 'name'
            EMAIL = 'email'
            CREATEDAT = 'created_at'
            LASTACTIVEAT = 'last_active_at'
    
    class ErrorMessage:
        class General(StrEnum):
            MEDIATYPE = 'Only json is allowed as request body'
            REQUIRED = 'The field {field} is required'
        
        class User:
            class Name(StrEnum):
                LENGTH = 'The length of name can be between {min} to {max} characters'.format(min=CurrentConfiguration.MIN_USERNAME_LENGTH,max=CurrentConfiguration.MAX_USERNAME_LENGTH)
                CONTAIN = 'The username can only contain "{contain}"'.format(contain=CurrentConfiguration.USERNAME_CAN_CONTAIN)
            
            class CreatedAt(StrEnum):
                CONSTANT = 'The field is constant'
            
            class LastActiveAt(StrEnum):
                CONFLICT = 'The last date activity is conflicting'

        class Controller(StrEnum):
            """Error Messages by controllers
            """
            EXISTS = 'User is already present in database'
            # NOT_FOUND = 'User not found in database'
            INVALID_OTP = 'The given OTP is invalid'
