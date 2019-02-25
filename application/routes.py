from application import application_instance, db
from application.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm
from application.models import User, Post
from application.email import send_password_reset_email
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime


@application_instance.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@application_instance.route('/', methods=['GET', 'POST'])
@application_instance.route('/index', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.post_title.data, body=form.post_body.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post was saved in database!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    if current_user.is_authenticated:
        posts = current_user.followed_posts().paginate(
            page, application_instance.config['POSTS_PER_PAGE'], False)
    elif current_user.is_anonymous:
        posts = Post.query.filter_by(deleted=False).order_by(Post.timestamp.desc()).paginate(
            page, application_instance.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html',
                           title='Home',
                           posts=posts.items,
                           form=form,
                           next_url=next_url,
                           prev_url=prev_url)


@application_instance.route('/explore')
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(deleted=False).order_by(Post.timestamp.desc()).paginate(
        page, application_instance.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html',
                           title='Explore',
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url)


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


@application_instance.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password.')
        return redirect(url_for('login'))
    return render_template('request_password_reset.html', title='Request New Password', form=form)


@application_instance.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password was successfully changed.')
        return redirect(url_for('index'))
    return render_template('reset_password.html', title='Reset Password', form=form)


@application_instance.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author=user, deleted=False).order_by(Post.timestamp.desc()).paginate(
        page, application_instance.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=username, page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html',
                           title='User Profile',
                           user=user,
                           posts=posts.items,
                           prev_url=prev_url,
                           next_url=next_url)


@application_instance.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.about_me = form.about_me.data
        current_user.username = form.username.data
        current_user.skype = form.skype.data
        current_user.facebook = form.facebook.data
        current_user.telegram = form.telegram.data
        db.session.commit()
        flash('Edit profile form has been saved.')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.about_me.data = current_user.about_me
        form.username.data = current_user.username
        form.skype.data = current_user.skype
        form.facebook.data = current_user.facebook
        form.telegram.data = current_user.telegram
    return render_template('edit_profile.html', title="Edit Profile Data", form=form)


@application_instance.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {} now!'.format(username))
    return redirect(url_for('user', username=username))


@application_instance.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}'.format(username))
    return redirect(url_for('user', username=username))


@application_instance.route('/post/<id>')
def post(id):
    post = Post.query.filter_by(id=id).first_or_404()
    return render_template('post_detail.html', post=post)


@application_instance.route('/post/<id>/delete', methods=['GET', 'POST'])
@login_required
def post_delete(id):
    post = Post.query.filter_by(id=id).first()
    if post is None:
        flash('Post with id {} not found :('.format(id))
        return redirect(url_for('index'))
    if post.author != current_user:
        flash('You are not author of this post!')
        return redirect(url_for('post', id=id))
    elif post.author == current_user:
        post.deleted = True
        db.session.commit()
        flash('Post {} ({}) deleted.'.format(id, post.title))
        return redirect(url_for('index'))
