from random import randint
from flask_mail import Message
from Application import mail, ErrorMessage
from werkzeug import exceptions

EmailError = ErrorMessage.User.Email

def send_otp(*,to_address):
    otp = ''.join([str(randint(0,9)) for _ in range(4)])
    msg = Message("OTP from MakeMyJob", recipients=[to_address])
    msg.body = f"Your OTP for MakeMyJob account is {otp}. Don't share this to anyone"
    mail.send(msg)
    return otp


def send_otp_for_test(*,to_address):
    return '0000'
