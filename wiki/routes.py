from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import current_user, login_user, logout_user
from sqlalchemy import func
from html import escape

from app import login, db
from app.utils.decor import login_required, fresh_login_required, anonymous_required
from app.utils.creole_func import creole2html

from . import bp
from .forms import WikiAddForm, WikiModifyForm
from .models import WikiArticle, WikiHistory

@bp.route('/')
def homepage():
    articles = WikiArticle.query.all()
    return render_template('wiki/homepage.html', articles=articles)

@bp.route('/read/<string:title>')
def read(title):
    article = WikiArticle.query.filter(func.lower(WikiArticle.title) == func.lower(title)) \
                               .first_or_404()
    return render_template('wiki/read.html',
                           title=article.title,
                           content=creole2html(article.history[-1].content) \
                                   if 'source' not in request.args \
                                   else escape(article.history[-1].content).replace('\n', '<br>'),
                           source='source' in request.args)
                           
@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = WikiAddForm()
    if not current_user.can_write_wiki:
        flash('You are not allowed to write wiki article.')
    elif request.method == 'POST' and form.validate():
        return redirect(url_for('wiki.modify', title=form.title.data))
    return render_template('wiki/add.html', form=form)
                           
@bp.route('/modify/<string:title>', methods=['GET', 'POST'])
@login_required
def modify(title):
    form = WikiModifyForm()
    article = WikiArticle.query.filter(func.lower(WikiArticle.title) == func.lower(title)) \
                               .first()
    previewed = False
    new_article = article is None
    
    if not current_user.can_write_wiki:
        flash('You are not allowed to write wiki article.')
    elif request.method == 'POST' and form.validate():
        if form.submit_add.data:
            if new_article or form.content.data != article.history[-1].content:
                action = 'unknown'
                if new_article:
                    action = 'add'
                    article = WikiArticle(title=title)
                    db.session.add(article)
                else:
                    action = 'edit'
                    if current_user.is_admin:
                        article.title = form.title.data
                db.session.commit()
                    
                history = WikiHistory(
                        user_uuid=current_user.uuid,
                        article_id=article.id,
                        content=form.content.data,
                        action=action,
                        remarks=form.remarks.data)
                db.session.add(history)
                db.session.commit()
                return redirect(url_for('wiki.read', title=article.title))
            flash('The contents are the same.')
        previewed = True
        
    form.title.data = title if new_article else form.title.data or article.title
    if not previewed:
        form.content.data = '' if new_article else article.history[-1].content
    
    return render_template('wiki/modify.html', form=form, title=form.title.data,
                           content=form.content.data, content_md=creole2html(form.content.data, to_read=1),
                           previewed=previewed, new=article is None)
                           
@bp.route('/history')
def history_list_all():
    histories = WikiHistory.query.order_by(WikiHistory.datetime.desc()).all()
    if histories is None:
        abort(404)
    return render_template('wiki/history_list.html',
                           title='Full history',
                           histories=histories)
                           
@bp.route('/history_id/<int:id>')
def history_id(id):
    history = WikiHistory.query.filter_by(id=id).first_or_404()
    title = history.WikiArticle.title
    order_id = history.WikiArticle.history.index(history) + 1
    return redirect(url_for('wiki.history_read', title=title, order_id=order_id))

@bp.route('/history/<string:title>')
def history_list(title):
    article = WikiArticle.query.filter(func.lower(WikiArticle.title) == func.lower(title)) \
                               .first_or_404()
    return render_template('wiki/history_list.html',
                           title=article.history[-1].WikiArticle.title,
                           histories=article.history[::-1])
                           
@bp.route('/history/<string:title>/<int:order_id>')
def history_read(title, order_id):
    article = WikiArticle.query.filter(func.lower(WikiArticle.title) == func.lower(title)) \
                               .first_or_404()
    if order_id - 1 not in range(len(article.history)):
        abort(404)
    return render_template('wiki/history_read.html',
                           title=article.title,
                           content=creole2html(article.history[order_id-1].content, to_read=2) \
                                   if 'source' not in request.args \
                                   else escape(article.history[order_id-1].content).replace('\n', '<br>'),
                           source='source' in request.args,
                           order_id=order_id,
                           order_max=len(article.history))