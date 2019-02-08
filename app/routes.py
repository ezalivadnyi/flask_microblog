from app import app
from flask import render_template
from app.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Eugene'}
    posts = [
        {
            'author': {'username': "John Lennon"},
            'body': "Let's see how it works."
        },
        {
            'author': {'username': 'Britney Spears'},
            'body': "Oh baby, baby! I'm rock!"
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)


@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title="Sign In", form=form)
