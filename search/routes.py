from flask import render_template, request, g, current_app, url_for
from flask_login import current_user

from app import db
from app.wiki.models import WikiArticle
from app.forum.models import ForumPost

from . import bp
from .forms import SearchForm

@bp.route('/', methods=['GET'])
def search():
    if 'q' not in request.args or not request.args.get('q', ''):
        return render_template('search/search.html')
    num_posts = min(request.args.get('limit', 10), 50)
    query = request.args.get('q', '')
    wiki_articles = WikiArticle.query.search(query).all()
    forum_posts = ForumPost.query.search(query).filter_by(readable=True).all()
    return render_template('search/result.html', query=query,
                           wiki_articles=wiki_articles,
                           forum_posts=forum_posts)