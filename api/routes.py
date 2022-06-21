from flask import current_app
from mcstatus import MinecraftServer as mcs
import json

from app import db
from app.utils.server import MinecraftServerLocal as msl

from . import bp

class EmptyQuery:
    raw = dict()
    
@bp.route('/')
def root():
    return 'Welcome to the API of this website.'

@bp.route('/server')
def server():
    if msl.is_on():
        mc = mcs.lookup(current_app.config['SERVER_IP'])
        try:
            query = mc.query()
        except:
            query = EmptyQuery()
        try:
            status = mc.status()
            return {'online': 'true', 'status': {**status.raw}, 'query': {**query.raw}}
        except Exception as e:
            return {'online': 'unknown', 'error': type(e).__name__}
    return {'online': 'false', 'startable': 'false' if msl.is_on() else 'true'}