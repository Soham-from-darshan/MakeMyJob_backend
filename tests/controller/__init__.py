from Application import EnumStore

ErrorSchema = EnumStore.JSONSchema.Error
UserSchema = EnumStore.JSONSchema.User

valid_name = 'Soham Jobanputra'
valid_email = 'sohamjobanputra7@gmail.com'

valid_user = {
	UserSchema.NAME.value : valid_name,
	UserSchema.EMAIL.value : valid_email
}

def check_error(msg: str, res: dict):
	assert res[ErrorSchema.DESCRIPTION.value] == msg


def signup(client): 
    res = client.post('/auth/getOTP',json=valid_user)
    token = res.json['token']
    res = client.post('/auth/login',headers={"Authorization":f'Bearer {token}'}, json={'otp':'0000'})
    return res.json['token']
