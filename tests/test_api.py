from Application import EnumStore
from werkzeug.http import HTTP_STATUS_CODES
from email_validator import validate_email, EmailNotValidError

ErrorSchema = EnumStore.JSONSchema.Error
UserSchema = EnumStore.JSONSchema.User

# we can use marshmellow to create objects and serialize it instead of creating dictionaries directly 
class TestAPI:
    """A class to test the API.
    """
    
    @staticmethod
    def testGetAllRoute(client):
        inputUser = {
            UserSchema.NAME.value : 'soham',
            UserSchema.EMAIL.value : 'sohamjobanputra7@gmail.com',
            UserSchema.PASSWORD.value : '12345678'            
        }
        
        response = client.get('/', follow_redirects=True)
        assert response.request.path == '/api/users'
        
        response = client.post('http://127.0.0.1:5000/api/users', data=inputUser)
        assert response.status_code == 200
        
        response = client.get('http://127.0.0.1:5000/api/users')
        assert response.status_code == 200

        assert len(response.json) == 1

        for key,val in inputUser.items():
            assert response.json[0][key] == val

        assert 'id' in response.json[0]
        assert type(response.json[0]['id']) == int
    
    
    @staticmethod
    def testNameErrors(nameTestCase: tuple[str,str], client):
        username, errorMessage = nameTestCase
        expectedError = {
            ErrorSchema.NAME.value: HTTP_STATUS_CODES[400],
            ErrorSchema.CODE.value: 400,
            ErrorSchema.DESCRIPTION.value : errorMessage
        }
        inputUser: dict = {
            UserSchema.NAME.value : username,
            UserSchema.EMAIL.value : "sohamjobanputra7@gmail.com",
            UserSchema.PASSWORD.value : "12345678"
        }
        
        response = client.post('http://127.0.0.1:5000/api/users', data=inputUser)
        assert response.status_code == 400
        assert response.json == expectedError
    
    
    @staticmethod
    def testPasswordErrors(passwordTestCase: tuple[str,str], client):
        password, errorMessage = passwordTestCase
        expectedError = {
            ErrorSchema.NAME.value: HTTP_STATUS_CODES[400],
            ErrorSchema.CODE.value: 400,
            ErrorSchema.DESCRIPTION.value : errorMessage
        }
        inputUser: dict = {
            UserSchema.NAME.value : 'soham',
            UserSchema.EMAIL.value : "sohamjobanputra7@gmail.com",
            UserSchema.PASSWORD.value : password
        }
        
        response = client.post('http://127.0.0.1:5000/api/users', data=inputUser)
        assert response.status_code == 400
        assert response.json == expectedError
    
    
    @staticmethod
    def testEmailErrors(client):
        testEmail = "bad email@gmail.com"
        inputUser = {
            UserSchema.NAME.value : 'soham',
            UserSchema.EMAIL.value : testEmail,
            UserSchema.PASSWORD.value : '12345678'
        }
        
        try:
            validate_email(testEmail,check_deliverability=False)
        except EmailNotValidError as e:
            expectedDescription = str(e)
        
        expectedError = {
            ErrorSchema.NAME.value : HTTP_STATUS_CODES[400],
            ErrorSchema.CODE.value : 400,
            ErrorSchema.DESCRIPTION.value : expectedDescription
        }
            
        response = client.post('http://127.0.0.1:5000/api/users', data=inputUser)
        assert response.status_code == 400
        assert response.json == expectedError
            