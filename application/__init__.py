from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

application_instance = Flask(__name__)
application_instance.config.from_object(Config)
db = SQLAlchemy(application_instance)
migrate = Migrate(application_instance, db)
login = LoginManager(application_instance)
login.login_view = 'login'

from application import routes, models
