from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from .extensions import db
import secrets

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_filenames = db.Column(db.Text)  # Comma-separated image filenames
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sent = db.Column(db.Boolean, default=False)  # Indicates if post has been included in a newsletter
    archived = db.Column(db.Boolean, default=False)  # Indicates if post has been archived

    def __repr__(self):
        return f"<Post {self.title}>"

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    unsubscribe_token = db.Column(db.String(100), unique=True, nullable=False)
    verification_token = db.Column(db.String(100), unique=True, nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, email):
        self.email = email
        self.unsubscribe_token = secrets.token_urlsafe(32)
        self.verification_token = secrets.token_urlsafe(32)
        self.is_verified = False

    def __repr__(self):
        return f"<Subscriber {self.email}>"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    newsletter_title = db.Column(db.String(128))
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    def __init__(self, username, email, password_hash, newsletter_title, verification_token=None):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.newsletter_title = newsletter_title
        if verification_token:
            self.verification_token = verification_token
        self.is_verified = False

    def __repr__(self):
        return f"<User {self.username}>"
