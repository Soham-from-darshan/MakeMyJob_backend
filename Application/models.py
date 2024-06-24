from flask import current_app
from Application import db, ErrorMessage
from sqlalchemy.orm import Mapped, mapped_column, validates
import datetime
from email_validator import validate_email, EmailNotValidError, EmailUndeliverableError

UserError = ErrorMessage.User

class ValidationError(Exception):
    pass

class User(db.Model): # type: ignore
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(nullable=False, default=datetime.datetime.now(),init=False)
    last_active_at: Mapped[datetime.date] = mapped_column(nullable=False, default=datetime.date.today(), init=False) 
        
    
    def nameValidator(self, key: str, value: str) -> str:
        value = value.strip()
        minn, maxx, containn = current_app.config['MIN_USERNAME_LENGTH'], current_app.config['MAX_USERNAME_LENGTH'], current_app.config['USERNAME_CAN_CONTAIN']  
        if  len(value) < minn or \
            len(value) > maxx:
                raise ValidationError(UserError.Name.LENGTH.value.format(min=minn, max=maxx))
        for char in value:
            if char not in containn:
                raise ValidationError(UserError.Name.CONTAIN.value.format(contain=containn))
        return value
    
    
    def emailValidator(self, key: str, value: str) -> str:
        try:
            email_info = validate_email(value,check_deliverability=True)
        except (EmailNotValidError, EmailUndeliverableError) as err:
            raise ValidationError(str(err))
        else:
            return email_info.normalized
    
    
    def createdatValidator(self, key: str, value: datetime.datetime) -> datetime.datetime:
        if self.created_at is not None:
            raise ValidationError(UserError.CreatedAt.CONSTANT.value)
        return value
    
    
    def lastactiveatValidator(self, key: str, value: datetime.date) -> datetime.date:        
        if self.last_active_at is not None and value < self.last_active_at:
            raise ValidationError(UserError.LastActiveAt.CONFLICT.value)
        return value
    
    columnWiseValidator = {
        'name' : nameValidator,
        'email' : emailValidator,
        'created_at' : createdatValidator,
        'last_active_at' : lastactiveatValidator
    }
    
    @validates('name', 'email', 'created_at', 'last_active_at')
    def validator(self, key: str, value):
        function = User.columnWiseValidator[key]
        return function(self,key,value) # type: ignore
