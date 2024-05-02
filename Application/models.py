from Application import db, EnumStore
from sqlalchemy.orm import Mapped, mapped_column, validates
# from marshmallow import Schema, fields, post_load, validate, validates, ValidationError
import datetime
from instance import DefaultConfiguration
import string
from werkzeug import exceptions
from email_validator import validate_email, EmailNotValidError

from icecream import ic # type: ignore

UserField = EnumStore.JSONSchema.User
UserError = EnumStore.ErrorMessage.User
GeneralError = EnumStore.ErrorMessage.General

class User(db.Model): # type: ignore
    """class to serialize, deserialize and validate the user model
    """
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    
    name: Mapped[str] = mapped_column(UserField.NAME, nullable=False)
    email: Mapped[str] = mapped_column(UserField.EMAIL, unique=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(UserField.CREATEDAT, nullable=False, default=datetime.datetime.now(),init=False)
    last_active_at: Mapped[datetime.date] = mapped_column(UserField.LASTACTIVEAT, nullable=False, default=datetime.date.today(), init=False) 
        
    
    def nameValidator(self, key: str, value: str) -> str:
        if not type(value) == str : raise exceptions.BadRequest(GeneralError.TYPE.value.format(type=str))
        value = value.strip()
        if  len(value) < (minimum:=DefaultConfiguration.MIN_USERNAME_LENGTH) or \
            len(value) > (maximum:=DefaultConfiguration.MAX_USERNAME_LENGTH):
                raise exceptions.BadRequest(UserError.Name.LENGTH.value.format(min=minimum,max=maximum))
        for char in value:
            if char not in string.ascii_letters:
                raise exceptions.BadRequest(UserError.Name.CONTAIN.value)
        return value
    
    
    def emailValidator(self, key: str, value: str) -> str:
        if not type(value) == str : raise exceptions.BadRequest(GeneralError.TYPE.value.format(type=str))
        try:
            email_info = validate_email(value,check_deliverability=False)
        except EmailNotValidError as err:
            raise exceptions.BadRequest(str(err))
        else:
            return email_info.normalized
    
    
    def createdatValidator(self, key: str, value: datetime.datetime) -> datetime.datetime:
        if not type(value) == datetime.datetime : raise exceptions.BadRequest(GeneralError.TYPE.value.format(type=datetime.datetime))
        if self.created_at is not None:
            raise exceptions.BadRequest(UserError.CreatedAt.CONSTANT.value)
        return value
    
    
    def lastactiveatValidator(self, key: str, value: datetime.date) -> datetime.date:
        if not type(value) == datetime.date : raise exceptions.BadRequest(GeneralError.TYPE.value.format(type=datetime.date))
        
        if self.last_active_at is not None and value < self.last_active_at:
            raise exceptions.BadRequest(UserError.LastActiveAt.CONFLICT.value)
        return value
    
    
    @validates(*UserField)
    def validator(self, key: str, value):
        fieldValidator = {
            UserField.NAME.value : self.nameValidator,
            UserField.EMAIL : self.emailValidator,
            UserField.CREATEDAT : self.createdatValidator,
            UserField.LASTACTIVEAT : self.lastactiveatValidator
        }
        return fieldValidator[key](key,value) # type: ignore