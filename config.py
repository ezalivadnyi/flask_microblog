import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    APPLICATION_NAME = 'Microblog'

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you_will_never_guess_this_key'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'microblog_sqlite.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER')  # 'smtp.googlemail.com' for Gmail
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)  # port 587 for Gmail TLS
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None  # 1 for Gmail
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_ADMINS = os.environ.get('MAIL_ADMINS')

    POSTS_PER_PAGE = 3
