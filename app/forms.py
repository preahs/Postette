from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectMultipleField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_wtf.file import MultipleFileField, FileAllowed
from wtforms.widgets import ListWidget, CheckboxInput
import os

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class SetupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    newsletter_title = StringField('Subject Line/Newsletter Title (this can be changed later)', validators=[DataRequired()])
    submit = SubmitField('Finish Setup')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    images = MultipleFileField('Images', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'bmp'], 'Images only!')
    ])
    videos = MultipleFileField('Videos', validators=[
        FileAllowed(['mp4', 'webm', 'mov'], 'Videos only!')
    ])
    submit = SubmitField('Create Post')

    def validate(self, extra_validators=None):
        # Custom validation for media size and type
        if not super().validate(extra_validators):
            return False

        # Check total size of all media (images + videos)
        total_size = 0
        MAX_TOTAL_SIZE = 15 * 1024 * 1024  # 15MB in bytes

        # Check images
        if self.images.data:
            for image in self.images.data:
                if image:
                    try:
                        image.seek(0, os.SEEK_END)
                        size = image.tell()
                        total_size += size
                        image.seek(0)
                    except Exception as e:
                        self.images.errors.append(f"Error processing image: {str(e)}")
                        return False

        # Check videos
        if self.videos.data:
            for video in self.videos.data:
                if video:
                    try:
                        video.seek(0, os.SEEK_END)
                        size = video.tell()
                        total_size += size
                        video.seek(0)
                    except Exception as e:
                        self.videos.errors.append(f"Error processing video: {str(e)}")
                        return False

        if total_size > MAX_TOTAL_SIZE:
            error_msg = f'Total size of all media (images and videos) must be less than 15MB. Current size: {total_size / (1024 * 1024):.2f}MB'
            self.images.errors.append(error_msg)
            return False

        return True

class SubscribeForm(FlaskForm):
    email = StringField('Your Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Subscribe')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Reset Password')