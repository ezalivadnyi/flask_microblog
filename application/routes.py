from application import application_instance, db
from application.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from application.models import User, Post
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
    if current_user.is_authenticated:
        posts = current_user.followed_posts().all()
    else:
        posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', title='Home', posts=posts, form=form)


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
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.timestamp.desc()).all()
    return render_template('user.html', title='User Profile', user=user, posts=posts)


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
        flash('Form has been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.about_me.data = current_user.about_me
        form.username.data = current_user.username
        form.skype.data = current_user.skype
        form.facebook.data = current_user.facebook
        form.telegram.data = current_user.telegram
    return render_template('edit_profile.html', title="Edit Profile", form=form)


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


@application_instance.route('/explore')
def explore():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', title='Explore', posts=posts)


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
        db.session.delete(post)
        db.session.commit()
        flash('Post {} ({}) deleted.'.format(id, post.title))
        return redirect(url_for('index'))
