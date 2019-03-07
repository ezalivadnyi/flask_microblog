from application import db
from application.blog.forms import EditProfileForm, PostForm
from application.models import User, Post
from application.translate import translate
from application.blog import bp
from flask import g, render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from datetime import datetime
from guess_language import guess_language


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
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
            return redirect(url_for('blog.index'))
        posts = current_user.followed_posts().paginate(
            page, current_app.config['POSTS_PER_PAGE'], False)
    elif current_user.is_anonymous:
        posts = Post.query.filter_by(deleted=False).order_by(Post.timestamp.desc()).paginate(
            page, current_app.config['POSTS_PER_PAGE'], False)
    first_url = url_for('blog.index', page=1)
    next_url = url_for('blog.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('blog.index', page=posts.prev_num) if posts.has_prev else None
    last_url = url_for('blog.index', page=posts.pages)
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


@bp.route('/explore')
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(deleted=False).order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    first_url = url_for('blog.explore', page=1)
    next_url = url_for('blog.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('blog.explore', page=posts.prev_num) if posts.has_prev else None
    last_url = url_for('blog.explore', page=posts.pages)
    return render_template('index.html',
                           title=_('Explore'),
                           posts=posts.items,
                           pages=posts.pages,
                           current_page=page,
                           first_url=first_url,
                           last_url=last_url,
                           next_url=next_url,
                           prev_url=prev_url)


@bp.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author=user, deleted=False).order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('blog.user', username=username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('blog.user', username=username, page=posts.prev_num) if posts.has_prev else None
    first_url = url_for('blog.user', username=username, page=1)
    last_url = url_for('blog.user', username=username, page=posts.pages)
    return render_template('user.html',
                           title=_('User Profile'),
                           user=user,
                           last_url=last_url,
                           first_url=first_url,
                           pages=posts.pages,
                           posts=posts.items,
                           prev_url=prev_url,
                           next_url=next_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
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
        return redirect(url_for('blog.user', username=current_user.username))
    elif request.method == 'GET':
        form.about_me.data = current_user.about_me
        form.username.data = current_user.username
        form.skype.data = current_user.skype
        form.facebook.data = current_user.facebook
        form.telegram.data = current_user.telegram
    return render_template('edit_profile.html', title=_("Edit Profile Data"), form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('blog.index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('blog.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s now!', username=username))
    return redirect(url_for('blog.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('blog.index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('blog.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s', username=username))
    return redirect(url_for('blog.user', username=username))


@bp.route('/post/<id>')
def post(id):
    post = Post.query.filter_by(id=id).first_or_404()
    return render_template('post_detail.html', post=post)


@bp.route('/post/<id>/delete', methods=['GET', 'POST'])
@login_required
def post_delete(id):
    post = Post.query.filter_by(id=id).first()
    if post is None:
        flash(_('Post with id %(id)s not found :(', id=id))
        return redirect(url_for('blog.index'))
    if post.author != current_user:
        flash(_('You are not author of this post!'))
        return redirect(url_for('blog.post', id=id))
    elif post.author == current_user:
        post.deleted = True
        db.session.commit()
        flash(_('Post %(id)s (%(title)s) deleted.', id=id, title=post.title))
        return redirect(url_for('blog.index'))


@bp.route('/translate', methods=['POST'])
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
