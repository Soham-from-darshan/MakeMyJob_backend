import pytest
from tests.model import nameValidationTestCases, get_model_obj
from Application.models import User, ValidationError
from Application import ErrorMessage
import datetime
from icecream import ic # type: ignore

# ic.disable()

UserErrorMessage = ErrorMessage.User
valid_email = 'sohamjobanputra7@gmail.com'
valid_name = 'Jobanputra Soham'

def testSerialization(app):
    obj = {
        'name' : valid_name,
        'email' : valid_email
    }
    user = get_model_obj(ModelClass=User, **obj).serialize()
    ic(user)
    assert type(user) == dict


class TestValidation:
    @staticmethod
    @pytest.mark.parametrize('name,err',nameValidationTestCases.items())
    def testName(name, err):
        obj = {
            'name' : name,
            'email' : valid_email
        }
        with pytest.raises(ValidationError) as err_info:
            get_model_obj(User, **obj)

        ic(str(err_info.value))
        assert str(err_info.value).split(':')[-1].strip() == err
    
    
    @staticmethod
    def testEmailValidationWorks():
        obj = {
            'name' : valid_name,
            'email' : 'bad email@gmail.com'
        }
        with pytest.raises(ValidationError):
            get_model_obj(User, **obj)
    
    
    @staticmethod
    def testUnmodifiableCreatedat():
        obj = {
            'name' : valid_name,
            'email' : valid_email
        }
        user = get_model_obj(User, **obj)
        with pytest.raises(ValidationError) as err_info:
            user.created_at -= datetime.timedelta(days=1)
        ic(str(err_info.value))
        assert str(err_info.value).split(':')[-1].strip() == UserErrorMessage.CreatedAt.CONSTANT.value

    
    @staticmethod
    def testLastActiveConflict():
        obj = {
            'name' : valid_name,
            'email' : valid_email
        }
        user = get_model_obj(User, **obj)
        user.last_active_at += datetime.timedelta(days=1)
        with pytest.raises(ValidationError) as err_info:
            user.last_active_at -= datetime.timedelta(days=1)
        ic(str(err_info.value))
        assert str(err_info.value).split(':')[-1].strip() == UserErrorMessage.LastActiveAt.CONFLICT.value
        