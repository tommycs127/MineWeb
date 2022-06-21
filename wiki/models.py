from app import db
from whoosh.analysis import StemmingAnalyzer
from datetime import datetime

class WikiArticle(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    
    history = db.relationship('WikiHistory', backref='WikiArticle', order_by='WikiHistory.datetime')
    
    __tablename__ = 'WikiArticle'
    __searchable__ = ['title']
    __analyzer__ = StemmingAnalyzer()
    
    def __repr__(self):
        return f'<WikiArticle {self.id}>'
        
class WikiHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    datetime = db.Column(db.DateTime, default=datetime.utcnow)
    user_uuid = db.Column(db.String, db.ForeignKey('User.uuid'), nullable=False)
    
    article_id = db.Column(db.String, db.ForeignKey('WikiArticle.id'), nullable=False)
    content = db.Column(db.String, nullable=False)
    
    action = db.Column(db.String, nullable=False)
    remarks = db.Column(db.String, default='')
    
    __tablename__ = 'WikiHistory'
    __searchable__ = ['content']
    __analyzer__ = StemmingAnalyzer()
    
    def __repr__(self):
        return f'<WikiHistory {self.id}>'