import pyotp
from uuid import UUID
import os
import json
from secrets import token_hex

from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user, login_user, logout_user

from app import login, db
from app.utils.auth import hashPassword, auth, auth_user, auth_password, auth_otp_code
from app.utils.decor import login_required, fresh_login_required, anonymous_required

from . import bp
from .forms import RegisterForm, LoginForm, RecoveryForm, SettingsForm
from .mcuuid import getOnlineUUID
from .models import User

def hasUUID(L, id):
    for i in L:
        if type(i) is dict and 'uuid' in i.keys() and i['uuid'] == id:
            return True
    return False

@login.user_loader
def load_user(uuid):
    return User.query.get(uuid)

@bp.route('/register', methods=['GET', 'POST'])
@anonymous_required
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate():
        user_uuid = str(UUID(getOnlineUUID(form.name.data)))
        user_name = form.name.data.lower()
        user = User(
                uuid=user_uuid,
                name=user_name,
                password_hash=hashPassword(form.password.data, token_hex(8)))
        db.session.add(user)
        db.session.commit()
        with open(os.path.join(current_app.config['SERVER_DIR'], 'whitelist.json'), mode='r+') as f:
            try:
                json_data = json.load(f)
                if not hasUUID(json_data, user_uuid): # If it's a new user
                    json_data.append({'uuid': user_uuid, 'name': user_name})
                    f.truncate(0) # Truncate content
                    f.seek(0) # Move cursor back to the first position
                    json.dump(json_data, f, indent=2)
            except:
                flash('Unexpected error occurred.')
                return render_template('auth/register.html', form=form)
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)
    
@bp.route('/login', methods=['GET', 'POST'])
@anonymous_required
def login():
    form = LoginForm()
    if request.method == 'POST':
        s = auth(form.name.data, form.password.data, form.otp_code.data)
        if s.success:
            login_user(s.user, remember=form.remember_me.data)
            return redirect(url_for('homepage.homepage'))
        else:
            flash(s.reason)
    return render_template('auth/login.html', form=form)
    
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage.homepage'))
    
@bp.route('/recovery', methods=['GET', 'POST'])
@anonymous_required
def recovery():
    form = RecoveryForm()
    if request.method == 'POST':
        user = User.query.filter_by(name=form.name.data.lower()).first()
        s = auth_otp_code(form.name.data, form.otp_code.data)
        if s.success:
            user.password_hash = hashPassword(form.password.data, token_hex(8))
            db.session.commit()
            return redirect(url_for('auth.login'))
        flash(s.reason)
    return render_template('auth/recovery.html', form=form)
                           
@bp.route('/settings', methods=['GET', 'POST'])
@fresh_login_required
def settings():
    form = SettingsForm()
    user = User.query.filter_by(name=current_user.name.lower()).first()
    if request.method == 'POST' and form.validate():
        if form.password_new.data:
            user.password_hash = hashPassword(form.password_new.data, token_hex(8))
            flash('Password updated!')
        if current_user.tfa_enabled and form.otp_disable.data and pyotp.TOTP(current_user.otp_secret).verify(form.otp_code.data):
            user.otp_secret = '!'
            flash('Two-factor authentication disabled!')
        elif not current_user.tfa_enabled and pyotp.TOTP(current_user.otp_secret[1:]).verify(form.otp_code.data):
            user.otp_secret = current_user.otp_secret[1:]
            flash('Two-factor authentication enabled!')
        db.session.commit()
        return redirect(url_for('auth.settings'))
    if current_user.otp_secret.startswith('!'):
        user.otp_secret = f'!{pyotp.random_base32()}'
        db.session.commit()
    return render_template('auth/settings.html', form=form)
