from Application import db, EnumStore, CurrentConfiguration as cfg
from sqlalchemy.orm import Mapped, mapped_column, validates
import datetime
from email_validator import validate_email, EmailNotValidError, EmailUndeliverableError

# from icecream import ic # type: ignore

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
        value = value.strip()
        if  len(value) < cfg.MIN_USERNAME_LENGTH or \
            len(value) > cfg.MAX_USERNAME_LENGTH:
                raise ValueError(UserError.Name.LENGTH.value)
        for char in value:
            if char not in cfg.USERNAME_CAN_CONTAIN:
                raise ValueError(UserError.Name.CONTAIN.value)
        return value
    
    
    def emailValidator(self, key: str, value: str) -> str:
        try:
            email_info = validate_email(value,check_deliverability=True)
        except (EmailNotValidError, EmailUndeliverableError) as err:
            raise ValueError(str(err))
        else:
            return email_info.normalized
    
    
    def createdatValidator(self, key: str, value: datetime.datetime) -> datetime.datetime:
        if self.created_at is not None:
            raise ValueError(UserError.CreatedAt.CONSTANT.value)
        return value
    
    
    def lastactiveatValidator(self, key: str, value: datetime.date) -> datetime.date:        
        if self.last_active_at is not None and value < self.last_active_at:
            raise ValueError(UserError.LastActiveAt.CONFLICT.value)
        return value
    
    columnWiseValidator = {
        UserField.NAME.value : nameValidator,
        UserField.EMAIL.value : emailValidator,
        UserField.CREATEDAT.value : createdatValidator,
        UserField.LASTACTIVEAT.value : lastactiveatValidator
    }
    
    @validates(*UserField)
    def validator(self, key: str, value):
        function = User.columnWiseValidator[key]
        return function(self,key,value) # type: ignore
