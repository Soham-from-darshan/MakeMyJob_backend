from flask import Blueprint, request, jsonify
from Application import EnumStore, db, jwt
from Application.models import User
from sqlalchemy.exc import IntegrityError
from werkzeug import exceptions
from flask_jwt_extended import current_user, jwt_required, create_access_token


bp = Blueprint('Auth',__name__, url_prefix='/auth')

HTTPMethod = EnumStore.HTTPMethod
UserScema = EnumStore.JSONSchema.User
ErrorMessage = EnumStore.ErrorMessage.Controller

@jwt.user_identity_loader
def user_identity_lookup(user: User):
    return user.id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()

def login_required():
	# update last active at
	pass

def get_user_data():
	pass

def check_data_consistancy():
	# check if user data is same as data in server
	pass

def check_email():
	pass


@bp.route('/register',methods=[HTTPMethod.POST.value])
def signup():
	rdata = request.get_json()
	name, email = rdata[UserScema.NAME.value], rdata[UserScema.EMAIL.value]
	user = User(name=name,email=email)
	db.session.add(user)
	try:
		db.session.commit()
	except IntegrityError:
		db.session.rollback()
		raise exceptions.BadRequest(ErrorMessage.EXISTS.value)
	# verify the email via otp
	return jsonify(token=create_access_token(identity=user))


@bp.route('/login',methods=[HTTPMethod.POST.value])
def login():
	rdata = request.get_json()
	email = rdata[UserScema.EMAIL.value]
	user = User.query.filter_by(email=email).one_or_none()
	if user is not None:
		# verify email via otp
		return jsonify(token=create_access_token(identity=user))

	name = rdata[UserScema.NAME.value]
	user = User(name=name,email=email) # also validates user
	db.session.add(user)
	# verify email via otp
	db.session.commit()
	return jsonify(token=create_access_token(identity=user))




def delete_account():
	pass

# background job
def delete_inactive_accounts():
	pass


@bp.route('/protected')
@jwt_required()
def protected_route():
	return current_user.serialize()