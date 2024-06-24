from instance import TestingConfiguration
from Application import ErrorMessage
from Application.models import User
from tests.controller import check_error, signup, valid_user, valid_email
from icecream import ic
from time import sleep
import datetime
from sqlalchemy import text
from instance.utils import send_otp

# ic.disable()


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


# @pytest.mark.skip(reason="I could't find way to check if the given email account exits")
# def test_signup_with_nonexisting_email(client):
#     nonexisting_email = 'hatimarchant77@gmail.com'
#     res = client.post('/auth/getOTP', json={'name':'hatim', 'email':nonexisting_email})
#     ic(res.json)
#     assert res.status_code == 400
#     check_error(ErrorMessage.User.Email.EXISTS.value(format=nonexisting_email))


def test_expired_otp(client): 
    res = client.post('/auth/getOTP',json=valid_user)
    token = res.json['token']
    OTP_EXPIRY = TestingConfiguration.OTP_EXPIRY_IN_MINUTES
    sleep(OTP_EXPIRY * 60)
    res = client.post('/auth/login',headers={"Authorization":f'Bearer {token}'}, json={'otp':'0000'})
    ic(res.json,res.status_code)
    assert res.json['description'] == 'Token has expired'


def test_login(client): 
    token = signup(client)
    res = client.post('/auth/getOTP',json={'email':valid_email})
    ic(res.json)
    assert res.status_code == 200
    token = res.json['token']
    res = client.post('/auth/login', headers={'Authorization':f'Bearer {token}'}, json={'otp':'0000'})
    ic(res.json)
    assert res.status_code == 200
    token = res.json['token']


def test_key_errorhandler(client):
    res = client.post('auth/getOTP', json=dict(name='Soham'))
    assert res.status_code == 400
    assert res.json['description'] == ErrorMessage.General.REQUIRED.value.format(field='email')


def test_validation_errorhandler(client):
    res = client.post('auth/getOTP', json=dict(name='$oham', email='sohamjobanputra7@gmail.com'))
    assert res.status_code == 400
    assert res.json['description'] == ErrorMessage.User.Name.CONTAIN.value.format(contain=TestingConfiguration.USERNAME_CAN_CONTAIN)


def test_last_active_at_changes(app, client, database):
    token = signup(client)
    two_days_ago = datetime.date.today() - datetime.timedelta(days=2)
    with app.app_context():
        conn = database.engine.connect()
        conn.execute(text('''
            UPDATE user
            SET last_active_at = :date 
            WHERE id = :id
        '''), dict(date=two_days_ago.isoformat(),id=1))
        conn.commit()
        database.session.commit()
        user = ic(database.session.get(User, ident=1))
    assert user.last_active_at == two_days_ago
    res = client.get('/account/getUser', headers=dict(Authorization=f'Bearer {token}'))
    assert res.status_code == 200
    assert res.json['last_active_at'] == datetime.date.today().strftime("%a, %d %b %Y %H:%M:%S GMT")


def test_send_mail(app):
    with app.app_context():
        otp = send_otp(to_address='sohamjobanputra7@gmail.com')
    assert type(otp) == str
    ic(otp)