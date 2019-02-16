from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from logging.handlers import SMTPHandler
import logging

application_instance = Flask(__name__)
application_instance.config.from_object(Config)
db = SQLAlchemy(application_instance)
migrate = Migrate(application_instance, db)
login = LoginManager(application_instance)
login.login_view = 'login'

# Logging errors by email
if not application_instance.debug:
    if application_instance.config['MAIL_SERVER']:
        auth = None
        if application_instance.config['MAIL_USERNAME'] or application_instance.config['MAIL_PASSWORD']:
            auth = (application_instance.config['MAIL_USERNAME'], application_instance.config['MAIL_PASSWORD'])
        secure = None
        if application_instance.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(application_instance.config['MAIL_SERVER'], application_instance.config['MAIL_PORT']),
            fromaddr='no-reply@' + application_instance.config['MAIL_SERVER'],
            toaddrs=application_instance.config['MAIL_ADMINS'],
            subject='Microblog Failure Report',
            credentials=auth,
            secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        application_instance.logger.addHandler(mail_handler)

from application import routes, models, errors
