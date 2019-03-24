from application import create_app, db, cli
from application.models import Post, User

app = create_app()
cli.register(app)


# Automatically add objects from dictionary to shell context.
# Fired with command 'flask shell'.
@app.shell_context_processor
def make_shell_context():
    app.app_context().push()
    return {
        'app': app,
        'db': db,
        'User': User,
        'Post': Post
    }
