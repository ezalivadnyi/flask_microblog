from application import db
from application.models import User
from application.auth import bp
from application.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from application.email import send_password_reset_email
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user
from flask_babel import _
from werkzeug.urls import url_parse


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash(_('You have already authenticated and redirected to index page.'))
        return redirect(url_for('blog.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password! Try again. :('))
            return render_template('login.html', title=_('Sign In'), form=form)

        login_user(user, remember=form.remember_me.data)
        flash(_('Login successful. Welcome back! :)'))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('blog.index')
        return redirect(next_page)

    return render_template('login.html', title=_('Sign In'), form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('blog.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash(_('You have already authenticated and redirected to index page.'))
        return redirect(url_for('blog.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        login_user(user)
        flash(_('You was automatically logged in with your credentials.'))
        return redirect(url_for('blog.index'))
    return render_template('register.html', title=_('Registration'), form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            send_password_reset_email(user)
        flash(_('Check your email for the instructions to reset your password.'))
        return redirect(url_for('auth.login'))
    return render_template('request_password_reset.html', title=_('Request New Password'), form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        flash(_('You must logout before reset your password!'))
        return redirect(url_for('blog.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        flash(_('Incorrect or expired token. Please try again.'))
        return redirect(url_for('blog.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password was successfully changed.'))
        return redirect(url_for('blog.index'))
    return render_template('reset_password.html', title=_('Reset Password'), form=form)
