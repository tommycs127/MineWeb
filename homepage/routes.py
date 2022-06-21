from flask import render_template, url_for, current_app
from . import bp

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

@bp.route('/')
@bp.route('/homepage')
def homepage():
    return render_template('homepage/homepage.html')
    
@bp.route('/sitemap')
def sitemap():
    links = []
    for rule in current_app.url_map.iter_rules():
        if 'GET' in rule.methods and has_no_empty_params(rule):
            u = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append(u)
    return str(set(sorted(links)))