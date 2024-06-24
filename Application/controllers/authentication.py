from flask import Blueprint, request, jsonify, current_app
from Application import ErrorMessage, db, get_expected_keys
from Application.models import User
from werkzeug import exceptions
from flask_jwt_extended import jwt_required, create_access_token, get_jwt, get_jwt_identity, verify_jwt_in_request   
import datetime
import functools
import instance.utils

bp = Blueprint('Auth',__name__, url_prefix='/auth')

ControllerError = ErrorMessage.Controller

def login_required():
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


@bp.route('/getOTP',methods=['POST'])
def get_otp():
    cipher = current_app.config['CIPHER']
    send_otp = getattr(instance.utils, current_app.config['SEND_OTP'])
    OTP_EXPIRY = current_app.config['OTP_EXPIRY_IN_MINUTES']

    rdata = request.get_json()
    email = get_expected_keys('email', json_request=rdata)
    user = User.query.filter_by(email=email).one_or_none()
    
    if user is not None:
        otp = send_otp(to_address=email)
        encrypted_otp = (cipher.encrypt(otp.encode())).decode()
        return jsonify(token=create_access_token(identity=user.id, expires_delta=datetime.timedelta(minutes=OTP_EXPIRY), additional_claims={'otp':encrypted_otp})) 

                       
    name = get_expected_keys('name', json_request=rdata)
    user = User(name=name,email=email) # validates new user

    otp = send_otp(to_address=email)
    encrypted_otp = (cipher.encrypt(otp.encode())).decode()
    return jsonify(token=create_access_token(identity=user.email, expires_delta=datetime.timedelta(minutes=OTP_EXPIRY), additional_claims={'otp':encrypted_otp,'usr':user.name}))



@bp.route('/login',methods=['POST'])
@jwt_required()
def login():
    cipher = current_app.config['CIPHER']

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

    raise exceptions.BadRequest(ControllerError.INVALID_OTP.value)
