from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import MappedAsDataclass, DeclarativeBase
from werkzeug import exceptions
from typing import cast
from enum import StrEnum
from instance import DefaultConfiguration as dcfg


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

def create_app(*,configClass: type) -> Flask:
    """Create WSGI application instance, apply given configuration. Initialize extensions and create database from models then register blueprints and a generic error handler to jsonify any defalut errors. Return app instance.

    Args:
        config (type): A class that represents app configurations. This class is instantiated and passed to Flask.config.from_object method.

    Returns:
        Flask: The WSGI application instance.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(configClass())

    db.init_app(app)
    import Application.models as models
    with app.app_context():
        db.create_all()    

    # register blueprints
    
    @app.before_request
    def check_json():
        if not request.is_json(): raise exceptions.UnsupportedMediaType(EnumStore.ErrorMessage.RequestError.MEDIATYPE.value)
    
    @app.errorhandler(exceptions.HTTPException)
    def jsonify_default_errors(e: exceptions.HTTPException):
        """Convert the default error pages to json with three fields: code, name and description. Use args as description, if InternalServerError is handled then description is set to original error's args if it exists. Code and name is set to error's default code and name. 

        Args:
            e (HTTPException): Error to handle 

        Returns:
            (data, code) (tuple): tuple of error as dictionary and HTTP status code 
        """
        code: int
        name: str
        description: str | list
        
        ErrorSchema = EnumStore.JSONSchema.Error
        if issubclass(type(e), exceptions.InternalServerError):
            UnhandledException = cast(exceptions.InternalServerError, e)
            if UnhandledException.original_exception is not None and any(args:=UnhandledException.original_exception.args):
                description = args[0] if len(args)==1 else list(args)
            else:
                description = UnhandledException.description
            
            name = UnhandledException.name
            code = UnhandledException.code
        else:
            description = e.description # type: ignore
            name = e.name
            code = e.code # type: ignore
                    
        data = {ErrorSchema.CODE.value:code, ErrorSchema.NAME.value:name, ErrorSchema.DESCRIPTION.value:description}
        return data, code
    
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
                LENGTH = 'The length of name can be between {min} to {max} characters'.format(min=dcfg.MIN_USERNAME_LENGTH,max=dcfg.MAX_USERNAME_LENGTH)
                CONTAIN = 'The username can only contain "{contain}"'.format(contain=dcfg.USERNAME_CAN_CONTAIN)
            
            class CreatedAt(StrEnum):
                CONSTANT = 'The field is constant'
            
            class LastActiveAt(StrEnum):
                CONFLICT = 'The last date activity is conflicting'