from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectMultipleField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import MultipleFileField, FileAllowed
from wtforms.widgets import ListWidget, CheckboxInput

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class SetupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    newsletter_title = StringField('Subject Line/Newsletter Title (this can be changed later)', validators=[DataRequired()])
    submit = SubmitField('Finish Setup')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RequestPasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    images = MultipleFileField('Images', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'bmp'], 'Images only!')
    ])
    submit = SubmitField('Create Post')

class SubscribeForm(FlaskForm):
    email = StringField('Your Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Subscribe')