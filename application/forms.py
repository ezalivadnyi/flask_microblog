from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Length, Email, EqualTo
from application.models import User


class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))


class RegistrationForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField(_l('Repeat Password'),
                              validators=[DataRequired(), EqualTo('password'), Length(min=8)])
    submit = SubmitField(_l('Register'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_l('Please use a different username.'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_l('Please use a different email address.'))


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


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('New Password'), validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired(), EqualTo('password'), Length(min=8)])
    submit = SubmitField(_l('Set This New Password'))
