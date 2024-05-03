# testing for last_activate
# testing for email uniquness

from Application import EnumStore
from Application.models import User

UserField = EnumStore.JSONSchema.User
ErrorMessage = EnumStore.ErrorMessage

NameErrorMessage = EnumStore.ErrorMessage.User.Name

nameValidationTestCases = {
    '    ' : NameErrorMessage.LENGTH.value,
    'x': NameErrorMessage.LENGTH.value,
    'f'*21 : NameErrorMessage.LENGTH.value,
    '$oham Jobanputra' : NameErrorMessage.CONTAIN.value
}