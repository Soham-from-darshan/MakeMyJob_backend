import pytest
from instance import TestingConfiguration
from Application import EnumStore
from Application.models import User
from werkzeug.http import HTTP_STATUS_CODES as hsc
from tests.controller import check_error, signup, valid_user, valid_email
from icecream import ic
import datetime
import base64
import json
from time import sleep

# ic.disable()


UserSchema = EnumStore.JSONSchema.User
ErrorMessage = EnumStore.ErrorMessage
ErrorSchema = EnumStore.JSONSchema.Error


OTP_EXPIRY = TestingConfiguration.OTP_EXPIRY_IN_MINUTES

def test_signup(client):
	res = client.post('/auth/getOTP',json=valid_user)
	ic(res.json)
	assert res.status_code == 200
	token = res.json['token']

	res = client.post('/auth/login',headers={"Authorization":f'Bearer {token}'}, json={'otp':'0000'})
	ic(res.json)
	assert res.status_code == 200
	token = res.json['token']


def test_signup_with_invalid_otp(client):
	res = client.post('/auth/getOTP',json=valid_user)
	token = res.json['token']

	res = client.post('/auth/login',headers={"Authorization":f'Bearer {token}'}, json={'otp':'1111'})
	ic(res.json)
	assert res.status_code == 400
	check_error(ErrorMessage.Controller.INVALID_OTP.value, res.json)


@pytest.mark.skip(reason="I could't find way to check if the given email account exits")
def test_signup_with_nonexisting_email(client):
    nonexisting_email = 'hatimarchant77@gmail.com'
    res = client.post('/auth/getOTP', json={UserSchema.NAME.value:'hatim', UserSchema.EMAIL.value:nonexisting_email})
    ic(res.json)
    assert res.status_code == 400
    check_error(ErrorMessage.User.Email.EXISTS.value(format=nonexisting_email))


def test_expired_otp(client): 
    res = client.post('/auth/getOTP',json=valid_user)
    token = res.json['token']

    sleep(OTP_EXPIRY * 60)
    res = client.post('/auth/login',headers={"Authorization":f'Bearer {token}'}, json={'otp':'0000'})
    ic(res.json,res.status_code)
    assert res.json[ErrorSchema.DESCRIPTION] == 'Token has expired'


def test_login(client): 
    token = signup(client)
    res = client.post('/auth/getOTP',json={UserSchema.EMAIL.value:valid_email})
    ic(res.json)
    assert res.status_code == 200
    token = res.json['token']
    
    res = client.post('/auth/login', headers={'Authorization':f'Bearer {token}'}, json={'otp':'0000'})
    ic(res.json)
    assert res.status_code == 200
    token = res.json['token']

