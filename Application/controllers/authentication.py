from flask import Blueprint, request, jsonify
from Application import EnumStore, db, jwt, mail, cipher
from Application.models import User
from sqlalchemy.exc import IntegrityError
from werkzeug import exceptions
from flask_jwt_extended import current_user, jwt_required, create_access_token
from flask_mail import Message
from random import randint
import datetime
from instance import DefaultConfiguration


bp = Blueprint('Auth',__name__, url_prefix='/auth')

HTTPMethod = EnumStore.HTTPMethod
UserScema = EnumStore.JSONSchema.User
ErrorMessage = EnumStore.ErrorMessage.Controller
OTP_EXPIRY = DefaultConfiguration.OTP_EXPIRY_IN_MINUTES


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


# @bp.route('/register',methods=[HTTPMethod.POST.value])
# def signup():
# 	rdata = request.get_json()
# 	name, email = rdata[UserScema.NAME.value], rdata[UserScema.EMAIL.value]
# 	user = User(name=name,email=email)
# 	db.session.add(user)
# 	try:
# 		db.session.commit()
# 	except IntegrityError:
# 		db.session.rollback()
# 		raise exceptions.BadRequest(ErrorMessage.EXISTS.value)
# 	# verify the email via otp
# 	return jsonify(token=create_access_token(identity=user))




@bp.route('/getOTP',methods=[HTTPMethod.POST.value])
def get_otp():
	rdata = request.get_json()
	email = rdata[UserScema.EMAIL.value]
	user = User.query.filter_by(email=email).one_or_none()
	if user is not None:
		otp = send_otp(to_address=email)
		encrypted_otp = cipher.encrypt(otp.encode('utf-8'))
		return jsonify(token=create_access_token(identity=user.email, 
												expires_delta=datetime.timedelta(minutes=OTP_EXPIRY),
												additional_claims={'otp':encrypted_otp,'sub':user.name}))

	name = rdata[UserScema.NAME.value]
	User(name=name,email=email) # to validate user
	otp = send_otp(to_address=email)
	encrypted_otp = cipher.encrypt(otp.encode('utf-8'))
	return jsonify(token=create_access_token(identity=user.email, 
											expires_delta=datetime.timedelta(minutes=15),
											additional_claims={'otp':encrypted_otp,'sub':user.name}))



@bp.route('/login',methods=[HTTPMethod.POST.value])
@jwt_required()
def login():
	claims, rdata = get_jwt(), request.get_json()
	requested_otp, encrypted_otp = rdata['otp'], claims['otp']
	original_otp = (cipher.decrypt(encrypted_otp)).decode('utf-8')

	if original_otp == requested_otp:
		email, name = get_jwt_identity(), claims['sub']
		user = User(email=email,name=name)
		db.session.add(user)
		try:
			db.session.commit()
		except IntegrityError: # if user already exists
			db.session.rollback()
		finally:			
			return jsonify(token=create_access_token(identity=user.id))

	raise exceptions.BadRequest(ErrorMessage.INVALID_OTP.value)  



def delete_account():
	pass

# background job
def delete_inactive_accounts():
	pass


@bp.route('/protected')
@jwt_required()
def protected_route():
	id = get_jwt_identity()
	user = User.query.get(id)
	if user is not None:
		return user.serialize()
	return exceptions.BadRequest(ErrorMessage.NOT_FOUND.value)



def send_otp(*,to_address):
	otp = ''.join([str(randint(0,9)) for _ in range(4)])
	msg = Message("OTP Verification from MakeMyJob", recipients=[to_address])
	msg.body = f"Your OTP for MakeMyJob account is {otp}. Don't share this to anyone"
	mail.send(msg)
	return otp