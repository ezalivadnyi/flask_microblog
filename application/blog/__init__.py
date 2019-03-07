from flask import Blueprint

bp = Blueprint('blog', __name__, template_folder='templates')

from application.blog import routes