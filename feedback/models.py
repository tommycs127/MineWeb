from app import db
from datetime import datetime

class Feedback(db.Model):
    key = db.Column(db.String, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    type_ = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    reply = db.Column(db.String, nullable=False, default='')
    
    __tablename__ = 'Feedback'

    def __repr__(self):
        return f'<Feedback {self.key}>'