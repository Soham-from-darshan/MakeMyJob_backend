import pytest
from Application import EnumStore
from Application.models import User
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

NameField = EnumStore.ErrorMessage.NameField
PasswordField = EnumStore.ErrorMessage.PasswordField
Field = EnumStore.JSONSchema.User

class TestUserModel:
    """A class to test the Declarative mapped class for User
    """
    
    @staticmethod
    def testNameValidation(nameTestCase):
        username, errorMessage = nameTestCase
        obj = {
            Field.EMAIL.value : 'example123@gmail.com',
            Field.PASSWORD.value : '12345678'
        }
        obj[Field.NAME.value] = username
        with pytest.raises(ValueError) as err:
            User(**obj)
        
        assert str(err.value) == errorMessage
    
        
    @staticmethod
    def testPasswordValidation(passwordTestCase):
        password, errorMessage = passwordTestCase
        obj = {
            Field.EMAIL.value : 'example123@gmail.com',
            Field.NAME.value : 'username123'
        }
        obj[Field.PASSWORD.value] = password
        with pytest.raises(ValueError) as err:
            User(**obj)
        
        assert str(err.value) == errorMessage
    
    @staticmethod
    def testEmailValidationWorks():
        obj = {
            Field.PASSWORD.value : '12345678',
            Field.NAME.value : 'username123'
        }
        obj[Field.EMAIL.value] = 'bad email @example.com'
        with pytest.raises(ValueError):
            User(**obj)
    
    @staticmethod
    def testUniqueEmail(database: SQLAlchemy):
        user1 = User(name='xyz123', email='sameemail@gmail.com', password='12345678')
        user2 = User(name='abc123', email='sameemail@gmail.com', password='aaaaaaaaa')
        database.session.add_all([user1, user2])
        with pytest.raises(IntegrityError):
            database.session.commit()
            