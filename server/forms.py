from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, IntegerField, HiddenField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

class SettingsForm(FlaskForm):
    message = TextAreaField('Message')
    startable = BooleanField('Startable')
    submit = SubmitField('Submit')