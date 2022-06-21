from flask import render_template, request, flash, redirect, url_for, current_app
from flask_login import current_user
import os

from app import db
from app.utils.decor import login_required, fresh_login_required, anonymous_required
from app.utils.server import MinecraftServerLocal as msl

from . import bp
from .forms import SettingsForm

@bp.route('/', methods=['GET', 'POST'])
def status():
    form = SettingsForm()
    if current_user.is_authenticated:
        if current_user.is_admin:
            if form.is_submitted:
                msl.set_message(form.message.data)
                db.session.commit()
            form.message.data = msl.message
        elif not current_user.can_start_server:
            flash('You are not allowed to start the server.')
        elif msl.is_on():
            if msl.message:
                flash(msl.message)
            else:
                flash('The server is not startable at the moment.')
    return render_template('server/status.html', form=form)
    
@bp.route('/start')
def start_server():
    if current_user.is_authenticated and current_user.can_start_server and not msl.is_on():
        msl.start()
    return redirect(url_for('server.status'))