from app import db
from sqlalchemy.orm import backref

from flask_login import UserMixin

class User(UserMixin, db.Model):
    uuid = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(16), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    permission = db.Column(db.Integer, nullable=False, default=0b11110)
    otp_secret = db.Column(db.String, nullable=True, default='!')
    
    wiki_author = db.relationship('WikiHistory', backref='User')
    forum_posts = db.relationship('ForumPost', backref='User')
    forum_comments = db.relationship('ForumComment', backref='User')
    forum_votes = db.relationship('ForumVote', backref='User')
    
    __tablename__ = 'User'
    
    def get_id(self):
        return self.uuid
        
    @property
    def tfa_enabled(self):
        return self.otp_secret and not self.otp_secret.startswith('!')
        
    @property
    def is_admin(self):
        '''
        If a user is admin, all restrictions will be overrided.
        '''
        return self.permission & 2**0
    
    @property
    def can_login(self):
        return self.is_admin or self.permission & 2**1
        
    @property
    def can_start_server(self):
        return self.is_admin or self.permission & 2**2
        
    @property
    def can_write_wiki(self):
        return self.is_admin or self.permission & 2**3
        
    @property
    def can_write_forum(self):
        return self.is_admin or self.permission & 2**4
    
    def __repr__(self):
        return f'<User {self.name}>'