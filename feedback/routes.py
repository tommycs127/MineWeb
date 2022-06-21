from flask import render_template, request, flash, abort, redirect, url_for
from flask_login import current_user
from secrets import token_hex

from app import db

from . import bp
from .forms import FeedbackSubmitForm, FeedbackSearchForm, FeedbackReplyForm
from .models import Feedback

@bp.route('/', methods=['GET', 'POST'])
def feedback():
    if current_user.is_authenticated and current_user.permission&0b1:
        feedbacks = Feedback.query.order_by(Feedback.timestamp.desc()).all()
        return render_template('feedback/list.html', feedbacks=feedbacks)

    submitForm = FeedbackSubmitForm()
    searchForm = FeedbackSearchForm()
    if request.method == 'POST':
        if submitForm.validate_on_submit():
            key = token_hex(8)
            while Feedback.query.filter_by(key=key).first():
                key = token_hex(8)
            feedback = Feedback(type_ = submitForm.type_.data,
                                content = submitForm.content.data,
                                key = key)
            db.session.add(feedback)
            db.session.commit()
            return redirect(url_for('feedback.feedback_reply', key=key))
            
        elif searchForm.validate_on_submit():
            key = searchForm.key.data
            return redirect(url_for('feedback.feedback_reply', key=key))
            
    return render_template('feedback/main.html', submitForm=submitForm, searchForm=searchForm)

@bp.route('/<string:key>', methods=['GET', 'POST'])
def feedback_reply(key):
    replyForm = FeedbackReplyForm()
    feedback = Feedback.query.filter_by(key=key).first()
    
    if feedback is None:
        abort(404)
    
    if current_user.is_authenticated and current_user.permission&0b1:
        if request.method == 'POST':
            feedback.reply = replyForm.content.data
            db.session.commit()
        replyForm.content.data = feedback.reply
        return render_template('feedback/reply.html', feedback=feedback, replyForm=replyForm)
        
    return render_template('feedback/reply.html', feedback=feedback, replyForm=None)