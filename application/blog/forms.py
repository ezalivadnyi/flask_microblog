from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Length
from application.models import User


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    telegram = StringField('Telegram', validators=[Length(max=32)])
    skype = StringField('Skype', validators=[Length(max=32)])
    facebook = StringField('Facebook', validators=[Length(max=140)])
    about_me = TextAreaField(_l('About Me'), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Save'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_l('This username is already in use. Please chose another.'))


class PostForm(FlaskForm):
    post_title = StringField(_l('Title'), validators=[DataRequired(), Length(max=60)])
    post_body = TextAreaField(_l('Body'), validators=[DataRequired(), Length(min=20)])
    submit = SubmitField(_l('Post it!'))
