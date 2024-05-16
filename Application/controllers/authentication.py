from flask import Blueprint, request, jsonify, current_app
from Application import EnumStore, db, jwt, mail, cipher
from Application.models import User
from sqlalchemy.exc import IntegrityError
from werkzeug import exceptions
from flask_jwt_extended import current_user, jwt_required, create_access_token, get_jwt, get_jwt_identity, verify_jwt_in_request
from flask_mail import Message
from random import randint
import datetime
from instance import DefaultConfiguration
import functools


bp = Blueprint('Auth',__name__, url_prefix='/auth')

HTTPMethod = EnumStore.HTTPMethod
UserScema = EnumStore.JSONSchema.User
ErrorMessage = EnumStore.ErrorMessage.Controller
OTP_EXPIRY = DefaultConfiguration.OTP_EXPIRY_IN_MINUTES


def login_required():
	# update last active at
	pass

# def get_user_data():
# 	pass

# def check_data_consistancy():
# 	# check if user data is same as data in server
# 	pass


def otp_required():
    def wrapper(fn):
        @functools.wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            
         	# if this is not present then key error will be raised by python and handled by error handlers
        	claims['otp']
        	claims['usr']
        	claims['sub']

        return decorator

    return wrapper


@bp.route('/getOTP',methods=[HTTPMethod.POST.value])
def get_otp():
	rdata = request.get_json()
	email = rdata[UserScema.EMAIL.value]
	user = User.query.filter_by(email=email).one_or_none()

	if user is None:
		name = rdata[UserScema.NAME.value]
		user = User(name=name,email=email) # validates user

	otp = send_otp(to_address=email)
	encrypted_otp = (cipher.encrypt(otp.encode())).decode()
	return jsonify(token=create_access_token(identity=user.email, 
											expires_delta=datetime.timedelta(minutes=OTP_EXPIRY),
											additional_claims={'otp':encrypted_otp,'usr':user.name}))



@bp.route('/login',methods=[HTTPMethod.POST.value])
@otp_required
def login():
	claims, rdata = get_jwt(), request.get_json()
	requested_otp, encrypted_otp = str(rdata['otp']), claims['otp']
	original_otp = (cipher.decrypt(encrypted_otp)).decode()

	if original_otp == requested_otp:
		email, name = get_jwt_identity(), claims['usr']
		user = User(email=email,name=name)
		db.session.add(user)
		try:
			db.session.commit()
		except IntegrityError: # if user already exists
			db.session.rollback()
		finally:			
			return jsonify(token=create_access_token(identity=user.id,expires_delta=False))

	raise exceptions.BadRequest(ErrorMessage.INVALID_OTP.value)  



# def delete_account():
# 	pass

# # background job
# def delete_inactive_accounts():
# 	pass


@bp.route('/protected')
@jwt_required()
def protected_route():
	id = get_jwt_identity()
	user = db.get_or_404(User, id)
	return user.serialize()
	


def send_otp(*,to_address):
	otp = ''.join([str(randint(0,9)) for _ in range(4)])
	msg = Message(f"{otp}", recipients=[to_address])
	msg.body = f"Your OTP for MakeMyJob account is {otp}. Don't share this to anyone"
	mail.send(msg)
	return otp