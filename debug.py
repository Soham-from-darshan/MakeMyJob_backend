# debug mode
from Application import create_app
from instance import DevelopmentConfiguration

if __name__ == '__main__':
    app = create_app(configClass=DevelopmentConfiguration)
    app.run(debug=True)
    # python debug.py