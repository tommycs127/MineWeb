import pyotp

from hashlib import sha256

from app import db
from app.auth.models import User

SHA256 = lambda s: sha256(bytes(s, encoding='ascii')).hexdigest()
hashPassword = lambda pw, salt: f'$SHA${salt}${SHA256(SHA256(pw)+salt)}'
checkPassword = lambda pw, hash: hash == hashPassword(pw, hash.split('$')[2])

class Status:
    def __init__(self, success:bool, code:int, reason:str='', user:User=None):
        self.success = success
        self.code = code
        self.reason = reason
        self.user = user

def auth(name:str, password:str, otp_code:str):
    s = auth_user(name)
    if not s.success:
        return s
    user = s.user

    s = auth_password(name, password)
    if not s.success:
        return s
        
    s = auth_otp_code(name, otp_code)
    if not s.success:
        return s
        
    return Status(True, 0, user=user)
    
def auth_user(name):
    user = User.query.filter_by(name=name.lower()).first()
    
    if user is None:
        return Status(False, 1, 'This name is not registered.')
        
    if not user.can_login:
        return Status(False, 2, 'This user is not allowed to login.')
        
    return Status(True, 0, user=user)

def auth_password(name, password):
    s = auth_user(name)
    if not s.success:
        return s
    user = s.user
    
    if not checkPassword(password, user.password_hash):
        return Status(False, 3, 'Invalid password.')
        
    return Status(True, 0, user=user)
    
def auth_otp_code(name, otp_code):
    s = auth_user(name)
    if not s.success:
        return s
    user = s.user
        
    if user.tfa_enabled and not pyotp.TOTP(user.otp_secret).verify(otp_code):
        return Status(False, 4, 'Invalid OTP code.')
    
    if not user.tfa_enabled and otp_code:
        return Status(False, 5, 'This user does not enable two-factor authentication.')
        
    return Status(True, 0, user=user)
