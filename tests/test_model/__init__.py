# testing for last_activate
# testing for email uniquness

from Application import EnumStore
from Application.models import User
from icecream import ic # type: ignore

UserField = EnumStore.JSONSchema.User
ErrorMessage = EnumStore.ErrorMessage

def testSerialization():
    user = User(name='Soham', email='sohamjobanputra7@gmail.com').serialize()
    assert type(user) == dict
    ic(user)