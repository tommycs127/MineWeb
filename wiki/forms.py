import re

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, IntegerField, HiddenField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models import WikiArticle

class WikiAddForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
    def validate_title(self, title):
        wikiArticle = WikiArticle.query.filter(WikiArticle.title.ilike(title.data)).first()
        if wikiArticle is not None:
            raise ValidationError('This article already exists.')
        if re.match('[\/.?=&:#]+', title.data):
            raise ValidationError('Invalid title.')
            
class WikiModifyForm(FlaskForm):
    title = StringField('Title')
    content = TextAreaField('Content', render_kw={'rows': 10, 'cols': 100}, validators=[DataRequired()])
    remarks = StringField('Remarks')
    submit_preview = SubmitField('Preview')
    submit_add = SubmitField('Submit')