# production mode
from Application import create_app
from instance import DeploymentConfiguration

wsgiapp = create_app(configClass=DeploymentConfiguration)
# gunicorn -w 8 'run:wsgiapp' 