from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, MultipleFileField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    groups = SelectMultipleField('Groups', coerce=int)
    images = MultipleFileField('Images', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
    submit = SubmitField('Create Post')
