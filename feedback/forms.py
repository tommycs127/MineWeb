from flask_wtf import FlaskForm
from wtforms import RadioField, StringField, TextAreaField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length

class FeedbackSubmitForm(FlaskForm):
    type_ = RadioField('Type', choices=[('User','Report User'),('Problem','Report problem')], default='User')
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
class FeedbackSearchForm(FlaskForm):
    key = StringField('Your Key', validators=[DataRequired()])
    submit = SubmitField('Search')

class FeedbackReplyForm(FlaskForm):
    content = TextAreaField('Content')
    submit = SubmitField('Submit')