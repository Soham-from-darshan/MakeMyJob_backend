from Application import ErrorMessage, create_app
from instance import TestingConfiguration

NameErrorMessage = ErrorMessage.User.Name

minn = TestingConfiguration.MIN_USERNAME_LENGTH
maxx = TestingConfiguration.MAX_USERNAME_LENGTH
containn = TestingConfiguration.USERNAME_CAN_CONTAIN

nameValidationTestCases = {
    '    ' : NameErrorMessage.LENGTH.value.format(min=minn, max=maxx),
    'x': NameErrorMessage.LENGTH.value.format(min=minn, max=maxx),
    'f'*21 : NameErrorMessage.LENGTH.value.format(min=minn, max=maxx),
    '$oham Jobanputra' : NameErrorMessage.CONTAIN.value.format(contain=containn)
}

def get_model_obj(ModelClass=None, **obj):
    app = create_app(configClass=TestingConfiguration)
    with app.app_context():
        return ModelClass(**obj)