from random import randint
from flask_mail import Message
from Application import mail, EnumStore
from werkzeug import exceptions

EmailError = EnumStore.ErrorMessage.User.Email

def send_otp(*,to_address):
    otp = ''.join([str(randint(0,9)) for _ in range(4)])
    msg = Message("OTP from MakeMyJob", recipients=[to_address])
    msg.body = f"Your OTP for MakeMyJob account is {otp}. Don't share this to anyone"
    try:
	    mail.send(msg)
    except ConnectionRefusedError:
        raise exceptions.BadRequest(EmailError.EXISTS.value.format(address=to_address)) 
    else:
        return otp


def send_otp_for_test(*,to_address):
    return '0000'
