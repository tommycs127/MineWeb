from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import current_user, login_user, logout_user
from datetime import datetime

from app import login, db
from app.utils.decor import login_required, fresh_login_required, anonymous_required

from . import bp
from .forms import ThreadAddForm, ThreadForm, PostForm, CommentForm, VoteForm
from .models import ForumThread, ForumPost, ForumComment, ForumVote

@bp.route('/')
@bp.route('/t')
def homepage():
    threads = ForumThread.query.all()
    threads = [thread for thread in threads if thread.can_read_by(current_user)]
    return render_template('forum/homepage.html', threads=threads)

'''
Thread
'''

@bp.route('/t/add', methods=['GET', 'POST'])
@login_required
def thread_add():
    if not current_user.is_admin:
        return redirect(url_for('forum.homepage'))

    form = ThreadAddForm()
    if form.validate_on_submit():
        thread = ForumThread(name=form.name.data, intro='',
                             readable=False, postable=False)
        db.session.add(thread)
        db.session.commit()
        return redirect(url_for('forum.thread_edit', thread_id=thread.id))
    return render_template('forum/thread_add.html', form=form)
    
@bp.route('/t/<int:thread_id>')
def thread(thread_id):
    thread = ForumThread.query.filter_by(id=thread_id).first_or_404()
    if not thread.can_read_by(current_user): abort(404)

    posts = ForumPost.query.filter_by(thread_id=thread_id) \
                           .order_by(ForumPost.datetime.desc()).all()
    posts = [post for post in posts if post.can_read_by(current_user)]
    return render_template('forum/thread.html', thread=thread, posts=posts)
    
@bp.route('/t/<int:thread_id>/edit', methods=['GET', 'POST'])
@login_required
def thread_edit(thread_id):
    thread = ForumThread.query.filter_by(id=thread_id).first_or_404()
    if not thread.can_read_by(current_user): abort(404)
    
    if not current_user.is_admin:
        return redirect(url_for('forum.thread', thread_id=thread.id))

    form = ThreadForm()
    if form.validate_on_submit():
        thread.name = form.name.data
        thread.intro = form.intro.data
        thread.readable = form.readable.data
        thread.postable = form.postable.data
        db.session.commit()
        return redirect(url_for('forum.thread', thread_id=thread.id))
        
    form.name.data = thread.name
    form.intro.data = thread.intro
    form.readable.data = thread.readable
    form.postable.data = thread.postable
    return render_template('forum/thread_edit.html', thread=thread, form=form)
    
'''
Post
'''
    
@bp.route('/t/<int:thread_id>/add', methods=['GET', 'POST'])
@login_required
def post_add(thread_id):
    thread = ForumThread.query.filter_by(id=thread_id).first_or_404()
    if not thread.can_read_by(current_user): abort(404)
    
    if not thread.can_post_by(current_user):
        return redirect(url_for('forum.thread', thread_id=thread.id))
    
    form = PostForm()
    if form.validate_on_submit():
            post = ForumPost(user_uuid=current_user.uuid,
                             thread_id=thread_id,
                             title=form.title.data,
                             content=form.content.data,
                             commentable=form.commentable.data,
                             votable=form.votable.data)
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('forum.post', post_id=post.id))
    return render_template('forum/post_add.html', thread=thread, form=form)
    
@bp.route('/p/<int:post_id>')
def post(post_id):
    post = ForumPost.query.filter_by(id=post_id).first_or_404()
    if not post.can_read_by(current_user): abort(404)
    
    comments = ForumComment.query.filter_by(post_id=post_id) \
                                 .order_by(ForumComment.datetime.asc()).all()
    comments = [comment for comment in comments if comment.can_read_by(current_user)]
                                 
    commentForm = CommentForm()
    return render_template('forum/post.html', thread=post.ForumThread,
                                              post=post, comments=comments,
                                              commentForm=commentForm)
    
@bp.route('/p/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def post_edit(post_id):
    post = ForumPost.query.filter_by(id=post_id).first_or_404()
    if not post.can_read_by(current_user): abort(404)
    
    if not (current_user.is_admin or post.is_released_by(current_user)):
        return redirect(url_for('forum.post', post_id=post_id))
    
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.commentable = form.commentable.data
        if current_user.is_admin:
            post.readable = form.readable.data
        db.session.commit()
        return redirect(url_for('forum.post', post_id=post_id))
        
    form.title.data = post.title
    form.content.data = post.content
    form.commentable.data = post.commentable
    if current_user.is_admin:
        form.readable.data = post.readable
    return render_template('forum/post_edit.html', thread=post.ForumThread,
                                                   post=post, form=form)
    
@bp.route('/p/<int:post_id>/delete')
@login_required
def post_delete(post_id):
    post = ForumPost.query.filter_by(id=post_id).first_or_404()
    if not post.can_read_by(current_user): abort(404)
    
    if not post.is_released_by(current_user):
        return redirect(url_for('forum.post', post_id=post_id))
        
    post.readable = False
    db.session.commit()
    
    return redirect(url_for('forum.thread', thread_id=post.ForumThread.id))
    
@bp.route('/p/<int:post_id>/vote', methods=['POST'])
@login_required
def post_vote(post_id):
    post = ForumPost.query.filter_by(id=post_id).first_or_404()
    if not post.can_read_by(current_user): abort(404)
    
    form = VoteForm()
    if form.is_submitted:
        if post.can_vote_by(current_user):
            vote = ForumVote.query.filter_by(user_uuid=current_user.uuid, post_id=post_id).first()
            if vote is None:
                vote = ForumVote(user_uuid=current_user.uuid, post_id=post_id)
                vote.score = 1 if form.upvote.data else -1
                db.session.add(vote)
            else:
                db.session.delete(vote)
            db.session.commit()
        else:
            form.message.errors.append('You cannot vote on this post.')
            
    return redirect(url_for('forum.post', post_id=post_id))
    
@bp.route('/p/<int:post_id>/comment', methods=['POST'])
@login_required
def post_comment(post_id):
    post = ForumPost.query.filter_by(id=post_id).first_or_404()
    if not post.can_read_by(current_user): abort(404)

    if post.can_comment_by(current_user):
        form = CommentForm()
        if form.validate_on_submit():
            comment = ForumComment(user_uuid=current_user.uuid,
                                   post_id=post_id,
                                   content=form.content.data)
            db.session.add(comment)
            db.session.commit()
    else:
        flash('You cannot leave comments in this post.')
        
    return redirect(url_for('forum.post', post_id=post_id))
    
'''
Comment
'''

@bp.route('/c/<int:comment_id>')
def comment(comment_id):
    comment = ForumComment.query.filter_by(id=comment_id).first_or_404()
    if not comment.can_read_by(current_user): abort(404)
    
    return redirect(url_for('forum.post', post_id=comment.ForumPost.id))

@bp.route('/c/<int:comment_id>/edit', methods=['GET', 'POST'])
@login_required
def comment_edit(comment_id):
    comment = ForumComment.query.filter_by(id=comment_id).first_or_404()
    if not comment.can_read_by(current_user): abort(404)
    
    if not (current_user.is_admin or comment.is_released_by(current_user)):
        return redirect(url_for('forum.post', post_id=comment.ForumPost.id))
    
    form = CommentForm()
    if form.validate_on_submit():
        comment.content = form.content.data
        if current_user.is_admin:
            comment.readable = form.readable.data
        db.session.commit()
        return redirect(url_for('forum.post', post_id=comment.ForumPost.id))
        
    post = comment.ForumPost
    thread = post.ForumThread
    
    form.content.data = comment.content
    if current_user.is_admin:
        form.readable.data = comment.readable
    return render_template('forum/comment_edit.html', thread=thread, post=post, form=form)
    
@bp.route('/c/<int:comment_id>/delete')
@login_required
def comment_delete(comment_id):
    comment = ForumComment.query.filter_by(id=comment_id).first_or_404()
    if not comment.can_read_by(current_user): abort(404)
    
    if comment.is_released_by(current_user):
        comment.readable = False
        db.session.commit()
        
    return redirect(url_for('forum.post', post_id=comment.ForumPost.id))
    
@bp.route('/c/<int:comment_id>/vote', methods=['POST'])
@login_required
def comment_vote(post_id):
    comment = ForumComment.query.filter_by(id=comment_id).first_or_404()
    if not comment.can_read_by(current_user): abort(404)
    
    form = VoteForm()
    if form.is_submitted:
        if comment.can_vote_by(current_user):
            vote = ForumVote.query.filter_by(user_uuid=current_user.uuid, comment_id=comment_id).first()
            if vote is None:
                vote = ForumVote(user_uuid=current_user.uuid, comment_id=comment_id)
            vote.datetime = datetime.utcnow
            
            if form.upvote.data:
                vote.score = 1
            elif form.downvote.data:
                vote.score = -1
            elif form.cancel.data:
                db.session.delete(vote)
            db.session.commit()
        else:
            form.message.errors.append('You cannot vote on this comment.')
            
    return redirect(url_for('forum.post', post_id=comment.ForumPost.id))