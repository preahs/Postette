from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

from . import db

# Association table for many-to-many relationship between Post and Group
post_group = db.Table('post_group',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    emails = db.Column(db.Text, nullable=False)  # Comma-separated list of emails

    def __repr__(self):
        return f"<Group {self.name}>"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_filenames = db.Column(db.Text)  # Comma-separated image filenames
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to groups
    groups = db.relationship('Group', secondary=post_group, backref=db.backref('posts', lazy='dynamic'))

    def __repr__(self):
        return f"<Post {self.title}>"

