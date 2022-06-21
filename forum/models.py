from app import db

from whoosh.analysis import StemmingAnalyzer

from datetime import datetime

class ForumVote(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    datetime = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_uuid = db.Column(db.String, db.ForeignKey('User.uuid'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('ForumPost.id'), default=None)
    comment_id = db.Column(db.Integer, db.ForeignKey('ForumComment.id'), default=None)
    score = db.Column(db.Integer, nullable=False)
    
    __tablename__ = 'ForumVote'
    
    def __repr__(self):
        return f'<ForumVote {self.id}>'
        
class ForumComment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    datetime = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_uuid = db.Column(db.String, db.ForeignKey('User.uuid'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('ForumPost.id'), nullable=False)
    content = db.Column(db.String, nullable=False)
    
    votes = db.relationship('ForumVote', backref='ForumComment')
    
    readable = db.Column(db.Boolean, default=True)
    votable = db.Column(db.Boolean, default=True)
    
    __tablename__ = 'ForumComment'
    
    def is_released_by(self, user):
        return user.is_authenticated and self.user_uuid == user.uuid
        
    def can_read_by(self, user):
        return user.is_authenticated and user.is_admin or self.readable
        
    def can_vote_by(self, user):
        return user.is_authenticated and user.is_admin or self.votable
    
    def __repr__(self):
        return f'<ForumComment {self.id}>'
    
class ForumPost(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    datetime = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_uuid = db.Column(db.String, db.ForeignKey('User.uuid'), nullable=False)
    thread_id = db.Column(db.Integer, db.ForeignKey('ForumThread.id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    
    comments = db.relationship('ForumComment', backref='ForumPost')
    votes = db.relationship('ForumVote', backref='ForumPost')
    
    top = db.Column(db.Boolean, default=False)
    readable = db.Column(db.Boolean, default=True)
    commentable = db.Column(db.Boolean, default=True)
    votable = db.Column(db.Boolean, default=True)
    
    __tablename__ = 'ForumPost'
    __searchable__ = ['title', 'content']
    __analyzer__ = StemmingAnalyzer()
    
    def is_released_by(self, user):
        return user.is_authenticated and self.user_uuid == user.uuid
        
    def can_read_by(self, user):
        return user.is_authenticated and user.is_admin or self.readable
        
    def can_comment_by(self, user):
        return user.is_authenticated and user.is_admin or self.commentable
        
    def can_vote_by(self, user):
        return user.is_authenticated and user.is_admin or self.votable
        
    def __repr__(self):
        return f'<ForumPost {self.id}>'
        
class ForumThread(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    intro = db.Column(db.String, default=None)
    
    posts = db.relationship('ForumPost', backref='ForumThread', order_by='ForumPost.datetime.desc()')
    
    readable = db.Column(db.Boolean, default=True)
    postable = db.Column(db.Boolean, default=True)
    
    __tablename__ = 'ForumThread'
    
    def can_read_by(self, user):
        return user.is_authenticated and user.is_admin or self.readable
        
    def can_post_by(self, user):
        return user.is_authenticated and user.is_admin or self.postable
    
    def __repr__(self):
        return f'<ForumThread {self.id}>'