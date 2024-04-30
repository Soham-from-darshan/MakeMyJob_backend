from Application import db, EnumStore
from sqlalchemy.orm import Mapped, mapped_column, validates
from typing import Annotated
from email_validator import validate_email, EmailNotValidError

Field = EnumStore.JSONSchema.User
ErrorMessage = EnumStore.ErrorMessage

class User(db.Model): # type: ignore
    """A declarative mapped class represting the user model for sqlalchemy ORM.

    Fields:
        id: primary key for database, not needed for instantiating model class
        name: username within 4 to 30 characters containing lowercase characters or digits or underscores. username cannot start with a digit or underscore
        email: unique email
        password: password within 8 to 16 characters containing no spaces
    
    Methods:
        validator: validates the input data
    
    Classes:
        ExceptionStatements: A collection of StrEnum that represents appropriate exception messages 
    """
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[Annotated[str, 30]] = mapped_column(Field.NAME.value)
    email: Mapped[Annotated[str, 320]] = mapped_column(Field.EMAIL.value,unique=True)
    password: Mapped[Annotated[str,16]] = mapped_column(Field.PASSWORD.value)
    
    @validates(*Field)
    def validator(self, key: str, value: str):
        # we can also put marshmellow logic here and add schema classes inside the User class
        # if the mapped class contais a lot of Field then we can create a dictionary of "field : validator" and call the appropriate validator for given field, we can directly use marshmellow as well
        if key == Field.NAME:
            value = value.strip()
            if value == '' : raise ValueError(ErrorMessage.NameField.EMPTY.value)
            if len(value) < 4 or len(value) > 30: raise ValueError(ErrorMessage.NameField.LENGTH.value)
            if value[0] in '1234567890_' : raise ValueError(ErrorMessage.NameField.STARTSWITH.value)
            for char in value:
                if not ((char.isalpha() and char.islower()) or (char in '1234567890_')): raise ValueError(ErrorMessage.NameField.CONTAIN.value)

        elif key == Field.EMAIL:
            try:
                emailinfo = validate_email(value, check_deliverability=False)
                value = emailinfo.normalized
            except EmailNotValidError as e:
                raise ValueError(str(e))

        elif key == Field.PASSWORD:
            # we can use the third parth module named password-validator for strong password checking 
            value = value.strip()
            if value == '' : raise ValueError(ErrorMessage.PasswordField.EMPTY.value)
            if len(value) < 8 or len(value) > 16 : raise ValueError(ErrorMessage.PasswordField.LENGTH.value)
            for char in value:
                if char.isspace() : raise ValueError(ErrorMessage.PasswordField.SPACE.value)      
                     
        return value
    
    