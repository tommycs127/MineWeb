from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, IntegerField, HiddenField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models import ForumThread

import re
import pyotp

class VoteForm(FlaskForm):
    message = HiddenField('')
    upvote = SubmitField('Upvote')
    downvote = SubmitField('Downvote')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    readable = BooleanField('Readable')
    submit = SubmitField('Submit')
    
    def validate_content(self, content):
        if content.data.isspace():
            raise ValidationError('The content is blank.')
    
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    readable = BooleanField('Readable')
    commentable = BooleanField('Commentable')
    votable = BooleanField('Votable')
    submit = SubmitField('Submit')
    
    def validate_title(self, title):
        if title.data.isspace():
            raise ValidationError('The title is blank.')
    
    def validate_content(self, content):
        if content.data.isspace():
            raise ValidationError('The content is blank.')
    
# Only for admins
class ThreadAddForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
    def validate_name(self, name):
        category = ForumThread.query.filter_by(name=name.data).first()
        if category is not None:
            raise ValidationError('This category already exists.')
        if re.match('[\/.?=&:#]+', name.data):
            raise ValidationError('Invalid category name.')

# Only for admins
class ThreadForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    intro = StringField('Introduction')
    readable = BooleanField('Readable')
    postable = BooleanField('Postable')
    submit = SubmitField('Submit')