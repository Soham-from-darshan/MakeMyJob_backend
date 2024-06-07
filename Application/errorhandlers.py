from werkzeug import exceptions
from Application import EnumStore
from typing import cast        
from Application import EnumStore

ErrorMessage = EnumStore.ErrorMessage

def jsonify_default_errors(e: exceptions.HTTPException):
    """Convert the default error pages to json with a description field. Use args as description, if InternalServerError is handled then description is set to original error's args if it exists. Code is set to error's default code. 

    Args:
        e (HTTPException): Error to handle 

    Returns:
        (data, code) (tuple): tuple of error as dictionary and HTTP status code 
    """
    code: int
    description: str | list
    
    ErrorSchema = EnumStore.JSONSchema.Error
    if issubclass(type(e), exceptions.InternalServerError):
        UnhandledException = cast(exceptions.InternalServerError, e)
        if UnhandledException.original_exception is not None and any(args:=UnhandledException.original_exception.args):
            description = args[0] if len(args)==1 else list(args)
        else:
            description = UnhandledException.description
        
        code = UnhandledException.code
    else:
        description = e.description # type: ignore
        code = e.code # type: ignore
                
    data = {ErrorSchema.DESCRIPTION.value:description}
    return data, code


def handle_value_error(e: ValueError):
    return jsonify_default_errors(exceptions.BadRequest(e.args[0]))

def handle_key_error(e: KeyError):
    return jsonify_default_errors(exceptions.BadRequest(ErrorMessage.General.REQUIRED.value.format(field=e.args[0])))
