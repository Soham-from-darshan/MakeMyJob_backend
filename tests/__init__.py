from Application import EnumStore

NameField = EnumStore.ErrorMessage.NameField
PasswordField = EnumStore.ErrorMessage.PasswordField

nameValidationTestCases: dict = {
    '  ' : NameField.EMPTY.value,
    ' l' : NameField.LENGTH.value,
    'xyz' : NameField.LENGTH.value,
    'x'*31 : NameField.LENGTH.value,
    'usernamewith$pecia|c@racter' : NameField.CONTAIN.value,
    'contains\n\tcannotstrip' : NameField.CONTAIN.value,
    '_private': NameField.STARTSWITH.value,
    '1stprime': NameField.STARTSWITH.value
}

passwordValidationTestCases: dict = {
    '' : PasswordField.EMPTY,
    '  ' : PasswordField.EMPTY,
    '123' : PasswordField.LENGTH,
    '12345678901234567' : PasswordField.LENGTH,
    'contains space' : PasswordField.SPACE
}