from Application import EnumStore
from werkzeug.http import HTTP_STATUS_CODES as hsc

ErrorSchema = EnumStore.JSONSchema.Error
UserSchema = EnumStore.JSONSchema.User

valid_name = 'Soham Jobanputra'
valid_email = 'sohamjobanputra7@gmail.com'

valid_user = {
	UserSchema.NAME.value : valid_name,
	UserSchema.EMAIL.value : valid_email
}

def check_error(code: int, msg: str, res: dict):
	assert res[ErrorSchema.CODE.value] == code
	assert res[ErrorSchema.NAME.value] == hsc[code]
	assert res[ErrorSchema.DESCRIPTION.value] == msg


def signup(client): 
    res = client.post('/auth/getOTP',json=valid_user)
    token = res.json['token']
    res = client.post('/auth/login',headers={"Authorization":f'Bearer {token}'}, json={'otp':'0000'})
    return res.json['token']
