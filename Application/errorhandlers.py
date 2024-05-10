from werkzeug import exceptions
from Application import EnumStore
from typing import cast        
        

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


def handle_value_error(e: ValueError):
    return jsonify_default_errors(exceptions.BadRequest(e.args[0]))

def handle_key_error(e: KeyError):
    return jsonify_default_errors(exceptions.BadRequest(f"{e.args[0]} is required"))