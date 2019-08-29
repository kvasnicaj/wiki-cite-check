from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(256), index=True)
    numLinks = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Search: {self.keyword}>'


class LinksLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(256), index=True)
    status = db.Column(db.Integer)
    wal = db.Column(db.String(1))
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<{self.keyword} : {self.status} -> {self.wal}>'

    def serialize(self):
        '''return link objects in response as JSON'''
        return {
            'id': self.id,
            'url': self.url,
            'status': self.status,
            'keyword': self.keyword,
            'wal': self.wal
        }
