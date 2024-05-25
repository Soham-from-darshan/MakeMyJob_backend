import pytest
from instance import TestingConfiguration
from Application import EnumStore
from werkzeug.http import HTTP_STATUS_CODES as hsc
from tests.controller import check_error
from icecream import ic
import datetime
import base64
import json
from time import sleep

# ic.disable()


UserSchema = EnumStore.JSONSchema.User
ErrorMessage = EnumStore.ErrorMessage
ErrorSchema = EnumStore.JSONSchema.Error

valid_name = 'Soham Jobanputra'
valid_email = 'sohamjobanputra7@gmail.com'

valid_user = {
	UserSchema.NAME.value : valid_name,
	UserSchema.EMAIL.value : valid_email
}

OTP_EXPIRY = TestingConfiguration.OTP_EXPIRY_IN_MINUTES

# use `pytest -vv -s -rA` , the -s flag will allow user input in stdin

def test_signup(client):
	res = client.post('/auth/getOTP',json=valid_user)
	ic(res.json)
	assert res.status_code == 200
	token = res.json['token']

	otp = input("\nEnter the OTP: ")

	res = client.post('/auth/login',headers={"Authorization":f'Bearer {token}'}, json={'otp':otp})
	ic(res.json)
	assert res.status_code == 200
	token = res.json['token']

	res = ic(client.get('/auth/protected',headers={"Authorization":f'Bearer {token}'}))
	ic(res.json, str(res))
	assert res.status_code == 200
	for key in valid_user:
		assert valid_user[key] == res.json[key]


def test_signup_with_invalid_otp(client):
	res = client.post('/auth/getOTP',json=valid_user)
	ic(res.json)
	assert res.status_code == 200
	token = res.json['token']

	otp = input("\nEnter the invalid OTP: ")

	res = client.post('/auth/login',headers={"Authorization":f'Bearer {token}'}, json={'otp':otp})
	ic(res.json)
	assert res.status_code == 400
	check_error(400, ErrorMessage.Controller.INVALID_OTP.value, res.json)


def test_expired_otp(client): 
    res = client.post('/auth/getOTP',json=valid_user)
    ic(res.json)
    assert res.status_code == 200
    token = res.json['token']
    ic(token)
    otp = input("\nEnter the invalid OTP: ")
    sleep(OTP_EXPIRY * 60)
    res = client.post('/auth/login',headers={"Authorization":f'Bearer {token}'}, json={'otp':otp})
    ic(res.json,res.status_code)
    res.json[ErrorSchema.DESCRIPTION] = 'Token has expired'

# TODO: pending tests:
#	- updating last active at field for user in each request : maybe we can create "user_required" decorator which will handle this for us
#	- customize errors from jwt extended i.e. creating decorator that will raise bad request when jwt-extended gives error = not required currently because its ok until jwt-extended sends 4** errors on its own that all we need right now


# def test_keyerror_handler(client):
# 	user = dict(**valid_user)
# 	user.pop(UserSchema.NAME.value)
# 	res = client.post('/auth/register', json=user)
# 	ic(res.json)
# 	assert res.status_code == 400
# 	check_error(400, ErrorMessage.General.REQUIRED.value.format(field=UserSchema.NAME.value), res.json)


# def test_valueerror_handler(client):
# 	user = dict(**valid_user)
# 	user[UserSchema.NAME.value] = 'x'
# 	res = client.post('/auth/register', json=user)
# 	ic(res.json)
# 	assert res.status_code == 400
# 	check_error(400, ErrorMessage.User.Name.LENGTH.value, res.json)



# def test_play_with_token(client):
# 	res = client.post('/auth/getOTP',json=valid_user)
# 	token = res.json['token']

# 	otp = input('\nEnter OTP: ')
# 	res = client.post('/auth/login',headers={"Authorization":f'Bearer {token}'}, json=dict(otp=otp))
# 	token = res.json['token']
	
# 	payload_dict = decode_token(token)
# 	ic(payload_dict)
# 	modified_payload = modify_payload(payload_dict)
# 	ic(modified_payload)
# 	token = encode_token(token.split('.')[0], json.dumps(modified_payload), token.split('.')[-1])

# 	res = client.get('/auth/protected',headers={"Authorization":f'Bearer {token}'})
# 	ic(res.json)


# def decode_token(token):
# 	jwt = token.split('.')
# 	header, payload, signature = [base64.b64decode(part.encode('utf-8') + b'==') for part in jwt]
# 	string_header, string_payload = header.decode('utf-8'), payload.decode('utf-8')
# 	payload_dict = json.loads(string_payload)
# 	return payload_dict


# def encode_token(header, payload, signature):
# 	payload = base64.b64encode(payload.encode('utf-8'))
# 	return header+ '.' + payload.decode('utf-8') + '.' + signature


# def modify_payload(payload):
# 	# payload['otp'] = 'X' + payload['otp'][1:]
# 	return payload
