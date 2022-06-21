from flask import render_template
from werkzeug.exceptions import HTTPException
from . import bp

@bp.app_errorhandler(HTTPException)
def errorHandler(error):
    return render_template('errors/error.html', code=error.code), error.code