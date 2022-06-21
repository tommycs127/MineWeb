from flask import Blueprint

bp = Blueprint('homepage', __name__)

from app.homepage import routes