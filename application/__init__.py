from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from config import Config
from logging.handlers import SMTPHandler, RotatingFileHandler
import logging
import os

application_instance = Flask(__name__)
application_instance.config.from_object(Config)
mail = Mail(application_instance)
db = SQLAlchemy(application_instance)
migrate = Migrate(application_instance, db)
login = LoginManager(application_instance)
login.login_view = 'login'

if not application_instance.debug:
    # Logging errors by email
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

    # Logging errors to file
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_hadler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
    file_hadler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_hadler.setLevel(logging.INFO)
    application_instance.logger.addHandler(file_hadler)
    application_instance.logger.setLevel(logging.INFO)
    application_instance.logger.info('Microblog startup')

from application import routes, models, errors
