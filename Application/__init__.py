from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import MappedAsDataclass, DeclarativeBase
from werkzeug import exceptions
from enum import StrEnum
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler
import datetime


class Base(MappedAsDataclass, DeclarativeBase):
    def serialize(self) -> dict:
        table = self.__table__
        result = {}
        for col in table.columns:
            col_name = str(col).split('.')[-1]
            result[col_name] = getattr(self, col_name)
        # return json.dumps(result, default=str) # for stringification
        return result

    
db: SQLAlchemy = SQLAlchemy(model_class=Base)
jwt: JWTManager = JWTManager()
mail: Mail = Mail()


def create_app(*,configClass: type) -> Flask:
    import Application.errorhandlers as errhndl
    import Application.models as models
    import Application.controllers.authentication as auth
    import Application.controllers.account as acc

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(configClass())
    
    app.register_error_handler(exceptions.HTTPException, errhndl.jsonify_default_errors)
    app.register_error_handler(models.ValidationError, errhndl.handle_validation_errors)

    mail.init_app(app)
    jwt.init_app(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()    

    app.register_blueprint(auth.bp)
    app.register_blueprint(acc.bp)

    if app.testing:
        @app.route('/throw_error/<value>')
        def simulate_internal_server_error(value):
            if value == 'single':
                raise Exception('Single arg')
            elif value == 'multi':
                raise Exception(*('Multi arg'.split()))
            elif value == 'none':
                raise Exception()

    def delete_inactive_accounts():
        print('Lol')
        with app.app_context():
            year_before_today = datetime.date.today() - datetime.timedelta(days=(app.config['ACCEPTABLE_INACTIVITY_IN_YEARS'] * 365))
            accounts_to_be_deleted = models.User.query.filter(models.User.last_active_at <= year_before_today).all()
            for account in accounts_to_be_deleted:
                db.session.delete(account)
            db.session.commit()

    if app.config['ENABLE_SCHEDULER']:
        scheduler = BackgroundScheduler()  
        scheduler.add_job(delete_inactive_accounts, 'interval', hours=app.config['INACTIVE_ACCOUNT_DELETION_INTERVAL_IN_HOURS'])
        scheduler.start()

    return app



class ErrorMessage:
    class General(StrEnum):
        MEDIATYPE = 'Only json is allowed as request body'
        REQUIRED = 'The field {field} is required'
    
    class Controller(StrEnum):
        INVALID_OTP = 'The given OTP is invalid'

    class User:
        class Name(StrEnum):
            LENGTH = 'The length of name can be between {min} to {max} characters'
            CONTAIN = 'The username can only contain "{contain}"'
        
        class CreatedAt(StrEnum):
            CONSTANT = 'The field is constant'
        
        class LastActiveAt(StrEnum):
            CONFLICT = 'The last date activity is conflicting'

        class Email(StrEnum):
            EXISTS = 'The email address for {address} does not exists'



def get_expected_keys(*keys: str, json_request = {}) -> list[str] | str:
    vals = []
    for key in keys:
        try:
            vals.append(json_request[key])
        except KeyError:
            raise exceptions.BadRequest(ErrorMessage.General.REQUIRED.value.format(field=key))
    return vals if len(vals) > 1 else vals[0]