import pytest
from Application import EnumStore
from werkzeug.http import HTTP_STATUS_CODES as hsc
from tests.controller import check_error
from icecream import ic
import datetime
import base64
import json

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

# def test_signup(client):
# 	for i in range(2):
# 		res = client.post('/auth/getOTP',json=valid_user)
# 		assert res.status_code == 200
# 		token = res.json['token']
# 		otp = input('\nEnter OTP: ')
# 		res = client.post('/auth/login',headers={"Authorization":f'Bearer {token}'}, json={'otp':otp})
# 		# ic(res.json)
# 		assert res.status_code == 200
# 		token = res.json['token']
# 		res = client.get('/auth/protected',headers={"Authorization":f'Bearer {token}'})
# 		ic(res.json)
# 		assert res.status_code == 200
# 		for key in valid_user:
# 			assert valid_user[key] == res.json[key]

		# TODO: pending tests:
		#	- test for cryptography.fernet.InvalidToken
		#	- test for incorrect otp
		#	- checking what happens if token is modified
		#	- creating a custom "otp_required" decorator
		# 	- properly studying flask jwt extended


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



def test_play_with_token(client):
	res = client.post('/auth/getOTP',json=valid_user)
	token = res.json['token']

	otp = input('\nEnter OTP: ')
	res = client.post('/auth/login',headers={"Authorization":f'Bearer {token}'}, json=dict(otp=otp))
	token = res.json['token']

	payload_dict = decode_token(token)
	ic(payload_dict)
	modified_payload = modify_payload(payload_dict)
	ic(modified_payload)
	token = encode_token(token.split('.')[0], json.dumps(modified_payload), token.split('.')[-1])

	res = client.get('/auth/protected',headers={"Authorization":f'Bearer {token}'})
	ic(res.json)


def decode_token(token):
	jwt = token.split('.')
	header, payload, signature = [base64.b64decode(part.encode('utf-8') + b'==') for part in jwt]
	string_header, string_payload = header.decode('utf-8'), payload.decode('utf-8')
	payload_dict = json.loads(string_payload)
	return payload_dict


def encode_token(header, payload, signature):
	payload = base64.b64encode(payload.encode('utf-8'))
	return header+ '.' + payload.decode('utf-8') + '.' + signature


def modify_payload(payload):
	payload['sub'] = 2
	return payload