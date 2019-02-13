from application import application_instance, db
from application.models import Post, User


# Automatically add objects from dictionary to shell context.
# Fired with command 'flask shell'.
@application_instance.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Post': Post
    }
