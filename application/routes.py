from application import application_instance, db
from application.forms import LoginForm, RegistrationForm
from application.models import User
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime


@application_instance.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@application_instance.route('/')
@application_instance.route('/index')
def index():
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
    return render_template('index.html', title='Home', posts=posts)


@application_instance.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You have already authenticated and redirected to index page.')
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password! Try again. :(')
            return render_template('login.html', title='Sign In', form=form)

        login_user(user, remember=form.remember_me.data)
        flash('Login successful. Welcome back! :)')
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@application_instance.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@application_instance.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You have already authenticated and redirected to index page.')
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        login_user(user)
        flash('You was automatically logged in with your credentials.')
        return redirect(url_for('index'))
    return render_template('register.html', title='Registration', form=form)


@application_instance.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'title': 'shshshshshsh shshshshshsh  shshshshshsh  shshshshshsh  shshshshshsh shshshshshshs hshshshshsh shshshshs', 'body': 'Test post body 1 Test post body 1 Test post body 1 Test post body 1 Test post body 1 Test post body 1 Test post body 1 Test post body 1 Test post body 1 Test post body 1 Test post body 1 Test post body 1 Test post body 1 Test post body 1 Test post body 1 Test post body 1 Test post body 1 '},
        {'author': user, 'title': 'Test post title 2', 'body': 'Test post body 2'},
        {'author': user, 'title': 'Test post title 3', 'body': 'Test post body 3'},
        {'author': user, 'title': 'Test post title 4', 'body': 'Test post body 4'},
        {'author': user, 'title': 'Test post title 5', 'body': 'Test post body 5'},
        {'author': user, 'title': 'Test post title 6', 'body': 'Test post body 6'},
    ]
    return render_template('user.html', title='User Profile', user=user, posts=posts)
