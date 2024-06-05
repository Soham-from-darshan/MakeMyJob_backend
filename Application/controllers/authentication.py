from flask import Blueprint, request, jsonify, current_app
from Application import EnumStore, db, jwt, mail, cipher, CurrentConfiguration
from Application.models import User
from sqlalchemy.exc import IntegrityError
from werkzeug import exceptions
from flask_jwt_extended import jwt_required, create_access_token, get_jwt, get_jwt_identity, verify_jwt_in_request   
from flask_mail import Message
from random import randint
import datetime
import functools
from icecream import ic
import instance.utils

bp = Blueprint('Auth',__name__, url_prefix='/auth')

HTTPMethod = EnumStore.HTTPMethod
UserScema = EnumStore.JSONSchema.User
ErrorMessage = EnumStore.ErrorMessage.Controller
OTP_EXPIRY = CurrentConfiguration.OTP_EXPIRY_IN_MINUTES
send_otp = getattr(instance.utils, CurrentConfiguration.SEND_OTP)


def login_required():
    """checks the presence of user in database and updates User.last_active_at if needed"""
    def wrapper(fn):
        @functools.wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            current_user = db.get_or_404(User, get_jwt_identity())
            if current_user.last_active_at != (today:=datetime.date.today()):
                current_user.last_active_at = today
                db.session.commit()

            return fn(*args, **kwargs)      
            
        return decorator

    return wrapper	


@bp.route('/getOTP',methods=[HTTPMethod.POST.value])
def get_otp():
    """sends the otp and token for given valid email, if email is unknown then verifies the given name in request and returns the token"""
    rdata = request.get_json()
    email = rdata[UserScema.EMAIL.value]
    user = User.query.filter_by(email=email).one_or_none()
    
    if user is not None:
        otp = send_otp(to_address=email)
        encrypted_otp = (cipher.encrypt(otp.encode())).decode()
        return jsonify(token=create_access_token(identity=user.id, expires_delta=datetime.timedelta(minutes=OTP_EXPIRY), additional_claims={'otp':encrypted_otp})) 

                       
    name = rdata[UserScema.NAME.value]
    user = User(name=name,email=email) # validates new user

    otp = send_otp(to_address=email)
    encrypted_otp = (cipher.encrypt(otp.encode())).decode()
    return jsonify(token=create_access_token(identity=user.email, expires_delta=datetime.timedelta(minutes=OTP_EXPIRY), additional_claims={'otp':encrypted_otp,'usr':user.name}))



@bp.route('/login',methods=[HTTPMethod.POST.value])
@jwt_required()
def login():    
    """return the token for login if otp is confirmed here"""
    claims, rdata = get_jwt(), request.get_json()
    requested_otp, encrypted_otp = str(rdata['otp']), claims['otp']
    original_otp = (cipher.decrypt(encrypted_otp)).decode()

    if original_otp == requested_otp:
        if 'usr' not in claims:
            return jsonify(token=create_access_token(identity=claims['sub'], expires_delta=False))

        email, name = get_jwt_identity(), claims['usr']
        user = User(email=email,name=name) # validates new user second time, don't know how to fix this
        db.session.add(user)
        db.session.commit()

        return jsonify(token=create_access_token(identity=user.id, expires_delta=False))

    raise exceptions.BadRequest(ErrorMessage.INVALID_OTP.value)
