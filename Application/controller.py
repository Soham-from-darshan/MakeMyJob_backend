from flask import Blueprint, request, jsonify, Response
from werkzeug import exceptions
from Application import db, models, EnumStore
from sqlalchemy.exc import IntegrityError

HTTPMethod = EnumStore.HTTPMethod
Field = EnumStore.JSONSchema.User

class UserController:
    """
    A class controller for user model. Defines model attributes and registers a simple blueprint with a getAll route. 
    
    Members:
        blueprint (Blueprint): collection of releted routes for UserView

    Functions:
        getAll() -> Response: A "getAll" api route for user model 
    """
    
    blueprint = Blueprint('User',__name__,url_prefix='/api')
    
    
    # always follow the below order for decorators if using staticmethod decorator along with route otherwise type error code for mypy
    # @staticmethod
    @blueprint.route('/users',methods=[HTTPMethod.GET, HTTPMethod.POST])
    def getAll() -> Response: # type: ignore
        """Return all users on GET request, store the user in database for post request if request is in valid format and contains valid data, otherwise respond with 400 status code.

        Raises:
            exceptions.BadRequest: If the shape or attribute of data is invalid or unique key constrain fails for email field.

        Returns:
            Response: A json containing all users, or respond with either 200 or 400 status code. 
        """
        if request.method == HTTPMethod.GET:
            users = db.session.query(models.User).all()
            return jsonify(users)
        
        for value in Field:
            if value not in request.form:
                raise exceptions.BadRequest(f"{value} is not present in request")
        
            
        try:
            newUser = models.User(
                name = request.form[Field.NAME],
                email = request.form[Field.EMAIL],
                password = request.form[Field.PASSWORD]
            )
            db.session.add(newUser)
            db.session.commit()
        except (IntegrityError, ValueError) as e:
            raise exceptions.BadRequest(description=e.args[0])
        else:
            return Response(status=200)
    