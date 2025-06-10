from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from . import db

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_filenames = db.Column(db.Text)  # Comma-separated image filenames
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sent = db.Column(db.Boolean, default=False)  # Indicates if post has been included in a newsletter

    def __repr__(self):
        return f"<Post {self.title}>"
