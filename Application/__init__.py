from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import MappedAsDataclass, DeclarativeBase
from werkzeug import exceptions
from typing import cast
from enum import StrEnum
from typing import NoReturn

class Base(MappedAsDataclass, DeclarativeBase):
    pass

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

    from Application.controller import UserController
    app.register_blueprint(UserController.blueprint)
    
    @app.route('/')
    def home():
        return redirect(url_for('User.getAll'))
    
    # This will only capture all subclasses of HTTPException, which means that other errors will be caught by flask and generate default 500 Internal server error which results in HTTPException, the original error will be available via e.original_exception
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
            PASSWORD = 'password'
    
    
    class ErrorMessage:
        """Collection of enums which represents error messages.
        """
        class NameField(StrEnum):
            EMPTY = 'Username cannot be empty string'
            LENGTH = 'Username must have minimum length of 4 and maximum of 30'
            STARTSWITH = 'Username cannot start with a digit or underscore'
            CONTAIN = 'Username can only contain lowercase characters or digits or underscores'
        
        class PasswordField(StrEnum):
            EMPTY = 'Password cannot be empty string'
            LENGTH = 'Password must have minimum length of 8 and maximum of 16'
            SPACE = 'Password cannot contain any white space'