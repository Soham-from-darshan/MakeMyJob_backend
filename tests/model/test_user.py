import pytest
from tests.model import nameValidationTestCases
from Application.models import User
from Application import EnumStore
import datetime
from icecream import ic # type: ignore

UserSchema = EnumStore.JSONSchema.User
UserErrorMessage = EnumStore.ErrorMessage.User
valid_email = 'sohamjobanputra7@gmail.com'
valid_name = 'Jobanputra Soham'

def testSerialization():
    obj = {
        UserSchema.NAME.value : valid_name,
        UserSchema.EMAIL.value : valid_email
    }
    user = User(**obj).serialize()
    assert type(user) == dict
    ic(user)

class TestValidation:
    @staticmethod
    @pytest.mark.parametrize('name,err',nameValidationTestCases.items())
    def testName(name, err):
        obj = {
            UserSchema.NAME.value : name,
            UserSchema.EMAIL.value : valid_email
        }
        with pytest.raises(ValueError) as err_info:
            User(**obj)
        
        assert str(err_info.value).split(':')[-1].strip() == err
    
    
    @staticmethod
    def testEmailValidationWorks():
        obj = {
            UserSchema.NAME.value : valid_name,
            UserSchema.EMAIL.value : 'bad email@gmail.com'
        }
        with pytest.raises(ValueError):
            User(**obj)
    
    
    @staticmethod
    def testUnmodifiableCreatedat():
        obj = {
            UserSchema.NAME.value : valid_name,
            UserSchema.EMAIL.value : valid_email
        }
        user = User(**obj)
        with pytest.raises(ValueError) as err_info:
            user.created_at -= datetime.timedelta(days=1)
        assert str(err_info.value).split(':')[-1].strip() == UserErrorMessage.CreatedAt.CONSTANT.value

    
    @staticmethod
    def testLastActiveConflict():
        obj = {
            UserSchema.NAME.value : valid_name,
            UserSchema.EMAIL.value : valid_email
        }
        user = User(**obj)
        user.last_active_at += datetime.timedelta(days=1)
        with pytest.raises(ValueError) as err_info:
            user.last_active_at -= datetime.timedelta(days=1)
        assert str(err_info.value).split(':')[-1].strip() == UserErrorMessage.LastActiveAt.CONFLICT.value
        