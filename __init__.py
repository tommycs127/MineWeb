from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_wtf import CSRFProtect
#from flask_moment import Moment
#from flask_babel import Babel

from app.config import Config
from app.utils.server import MinecraftServerLocal

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
bootstrap = Bootstrap()
csrf = CSRFProtect()
msl = MinecraftServerLocal()
#moment = Moment()
#babel = Babel()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    
    login.init_app(app)
    bootstrap.init_app(app)
    csrf.init_app(app)
    msl.init_app(app)
    #moment.init_app(app)
    #babel.init_app(app)
    
    from app.errors import bp as bp_errors
    app.register_blueprint(bp_errors)
    
    from app.api import bp as bp_api
    app.register_blueprint(bp_api, url_prefix='/api')
    
    from app.static import bp as bp_static
    app.register_blueprint(bp_static, url_prefix='/static')
    
    from app.homepage import bp as bp_homepage
    app.register_blueprint(bp_homepage)
    
    from app.auth import bp as bp_auth
    app.register_blueprint(bp_auth)
    
    from app.wiki import bp as bp_wiki
    app.register_blueprint(bp_wiki, url_prefix='/wiki')
    
    from app.forum import bp as bp_forum
    app.register_blueprint(bp_forum, url_prefix='/forum')
    
    from app.feedback import bp as bp_feedback
    app.register_blueprint(bp_feedback, url_prefix='/feedback')
    
    from app.search import bp as bp_search
    app.register_blueprint(bp_search, url_prefix='/search')
    
    from app.server import bp as bp_server
    app.register_blueprint(bp_server, url_prefix='/server')
    
    return app