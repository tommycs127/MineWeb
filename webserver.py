from flask_login import current_user, logout_user
from flask_whooshalchemy import search_index
from gevent.pywsgi import WSGIServer

from . import create_app, cli, db

from .wiki.models import WikiArticle
from .forum.models import ForumPost

app = create_app()
cli.register(app)

@app.cli.command()
def createdb():
    db.create_all()
    
@app.cli.command()
def run_with_gevent():
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
    
@app.before_request
def checkUserIsBanned():
    if current_user.is_authenticated and not current_user.can_login:
        logout_user(current_user)
    
@app.before_request
def reindex():
    search_index(app, WikiArticle)
    search_index(app, ForumPost)

@app.shell_context_processor
def make_shell_processor():
    return dict()
    
@app.context_processor
def context_processor():
    return {'website_name': app.config['WEBSITE_NAME'],
            'url_map': app.url_map}