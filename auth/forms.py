from flask_login import current_user
from flask_wtf import FlaskForm
from pyqrcode import create as qr_create
from wtforms import (StringField, TextAreaField, PasswordField, BooleanField,
                     IntegerField, HiddenField, SubmitField, FormField)
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length

from .models import User
from .mcuuid import getOnlineUUID

import pyotp
    
class RegisterForm(FlaskForm):
    name = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
            DataRequired(),
            Length(min=8)])
    password_confirm = PasswordField('Repeat Password', validators=[
            DataRequired(),
            EqualTo('password', message='Password does not match')])
    submit = SubmitField('Register')
    
    def validate_name(self, name):
        user = User.query.filter_by(name=name.data.lower()).first()
        if user is not None:
            raise ValidationError('This name is registered.')
        if getOnlineUUID(name.data) is None:
            raise ValidationError('This name is not a paid account for Minecraft.')

class LoginForm(FlaskForm):
    name = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    otp_code = StringField('OTP Code')
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')
            
class RecoveryForm(FlaskForm):
    name = StringField('Username', validators=[DataRequired()])
    otp_code = StringField('OTP code', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired()])
    password_confirm = PasswordField('Repeat New Password', validators=[
            DataRequired(),
            EqualTo('password', message='Password does not match')])
    submit = SubmitField('Confirm')
            
class SettingsForm(FlaskForm):
    password_old = PasswordField('Current Password', validators=[DataRequired()])
    password_new = PasswordField('New Password')
    password_confirm = PasswordField('Repeat New Password', validators=[
            EqualTo('password_new', message='Password does not match')])
    otp_disable = BooleanField('Disable two-factor authentication ')
    otp_code = StringField('OTP code')
    submit = SubmitField('Update')
    
    def validate_password_new(self, password_new):
        min = 8
        if password_new.data and len(password_new.data) < min:
            raise ValidationError(f'Field must be at least {min} characters long.')
    
    def validate_otp_code(self, otp_code):
        #if not current_user.tfa_enabled and not pyotp.TOTP(current_user.otp_secret[1:]).verify(otp_code.data):
            #raise ValidationError('Invalid OTP code')
        if current_user.tfa_enabled and not pyotp.TOTP(current_user.otp_secret).verify(otp_code.data):
            raise ValidationError('Invalid OTP code')
            
    def getOauth(self, appname, issuer, secret, **kwargs):
        s = f'otpauth://totp/{appname}:{current_user.name}?secret={secret}&issuer={issuer}'
        return qr_create(s).png_as_base64_str(**kwargs)
