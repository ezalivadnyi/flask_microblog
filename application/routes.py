from application import application_instance, db
from application.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm
from application.models import User, Post
from application.email import send_password_reset_email
from application.translate import translate
from flask import g, render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from flask_babel import _, get_locale
from werkzeug.urls import url_parse
from datetime import datetime
from guess_language import guess_language


@application_instance.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@application_instance.route('/', methods=['GET', 'POST'])
@application_instance.route('/index', methods=['GET', 'POST'])
def index():
    form = PostForm()
    page = request.args.get('page', 1, type=int)
    if current_user.is_authenticated:
        if form.validate_on_submit():
            language = guess_language(form.post_body.data)
            if language == 'UNKNOWN' or len(language) > 5:
                language = ''
            post = Post(title=form.post_title.data, body=form.post_body.data, author=current_user, language=language)
            db.session.add(post)
            db.session.commit()
            flash(_('Your post was saved in database!'))
            return redirect(url_for('index'))
        posts = current_user.followed_posts().paginate(
            page, application_instance.config['POSTS_PER_PAGE'], False)
    elif current_user.is_anonymous:
        posts = Post.query.filter_by(deleted=False).order_by(Post.timestamp.desc()).paginate(
            page, application_instance.config['POSTS_PER_PAGE'], False)
    first_url = url_for('index', page=1)
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    last_url = url_for('index', page=posts.pages)
    return render_template('index.html',
                           title=_('Home'),
                           posts=posts.items,
                           form=form,
                           pages=posts.pages,
                           current_page=page,
                           first_url=first_url,
                           last_url=last_url,
                           next_url=next_url,
                           prev_url=prev_url)


@application_instance.route('/explore')
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(deleted=False).order_by(Post.timestamp.desc()).paginate(
        page, application_instance.config['POSTS_PER_PAGE'], False)
    first_url = url_for('explore', page=1)
    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None
    last_url = url_for('explore', page=posts.pages)
    return render_template('index.html',
                           title=_('Explore'),
                           posts=posts.items,
                           pages=posts.pages,
                           current_page=page,
                           first_url=first_url,
                           last_url=last_url,
                           next_url=next_url,
                           prev_url=prev_url)


@application_instance.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash(_('You have already authenticated and redirected to index page.'))
        return redirect(url_for('index'))

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
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title=_('Sign In'), form=form)


@application_instance.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@application_instance.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash(_('You have already authenticated and redirected to index page.'))
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        login_user(user)
        flash(_('You was automatically logged in with your credentials.'))
        return redirect(url_for('index'))
    return render_template('register.html', title=_('Registration'), form=form)


@application_instance.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            send_password_reset_email(user)
        flash(_('Check your email for the instructions to reset your password.'))
        return redirect(url_for('login'))
    return render_template('request_password_reset.html', title=_('Request New Password'), form=form)


@application_instance.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        flash(_('You must logout before reset your password!'))
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        flash(_('Incorrect or expired token. Please try again.'))
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password was successfully changed.'))
        return redirect(url_for('index'))
    return render_template('reset_password.html', title=_('Reset Password'), form=form)


@application_instance.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author=user, deleted=False).order_by(Post.timestamp.desc()).paginate(
        page, application_instance.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=username, page=posts.prev_num) if posts.has_prev else None
    first_url = url_for('user', username=username, page=1)
    last_url = url_for('user', username=username, page=posts.pages)
    return render_template('user.html',
                           title=_('User Profile'),
                           user=user,
                           last_url=last_url,
                           first_url=first_url,
                           pages=posts.pages,
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
        flash(_('Edit profile form has been saved.'))
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.about_me.data = current_user.about_me
        form.username.data = current_user.username
        form.skype.data = current_user.skype
        form.facebook.data = current_user.facebook
        form.telegram.data = current_user.telegram
    return render_template('edit_profile.html', title=_("Edit Profile Data"), form=form)


@application_instance.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s now!', username=username))
    return redirect(url_for('user', username=username))


@application_instance.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s', username=username))
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
        flash(_('Post with id %(id)s not found :(', id=id))
        return redirect(url_for('index'))
    if post.author != current_user:
        flash(_('You are not author of this post!'))
        return redirect(url_for('post', id=id))
    elif post.author == current_user:
        post.deleted = True
        db.session.commit()
        flash(_('Post %(id)s (%(title)s) deleted.', id=id, title=post.title))
        return redirect(url_for('index'))


@application_instance.route('/translate', methods=['POST'])
def translate_text():
    id = request.form['id']
    if id and int(id) > 0:
        post = Post.query.get(id)
        if post is not None and post.language:
            return jsonify({'text': translate(
                post.body,
                post.language,
                g.locale
            )})
        else:
            return jsonify({'text': 'Post not found.'})
    return jsonify({'text': 'Incorrect id.'})
