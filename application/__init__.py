from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from config import Config
from logging.handlers import SMTPHandler, RotatingFileHandler
import logging
import os

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'login'
login.login_message = _l('Please login to access this page.')
mail = Mail()
moment = Moment()
babel = Babel()


def create_app(config_class=Config):
    application_instance = Flask(__name__)
    application_instance.config.from_object(config_class)

    db.init_app(application_instance)
    migrate.init_app(application_instance, db)
    login.init_app(application_instance)
    mail.init_app(application_instance)
    moment.init_app(application_instance)
    babel.init_app(application_instance)

    from application.errors import bp as errors_bp
    application_instance.register_blueprint(errors_bp)

    from application.auth import bp as auth_bp
    application_instance.register_blueprint(auth_bp, url_prefix='/auth')

    from application.blog import bp as blog_bp
    application_instance.register_blueprint(blog_bp)

    if not application_instance.debug and not application_instance.testing:
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
                subject=_l('Microblog Failure Report'),
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

    return application_instance


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


from application import models
