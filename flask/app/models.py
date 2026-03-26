"""Database models for PasteBoard."""

from flask_login import UserMixin
from . import db, login_manager


class User(UserMixin, db.Model):
    """Registered user account with role-based access."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="user")
    bio = db.Column(db.String(500), nullable=True)
    pastes = db.relationship("Paste", backref="author", lazy=True)


class Paste(db.Model):
    """A code paste/snippet created by a user."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(50), default="text")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    is_private = db.Column(db.Boolean, default=False)
    comments = db.relationship(
        "Comment", backref="paste", lazy=True, cascade="all, delete-orphan"
    )


class Comment(db.Model):
    """A comment on a paste."""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    posted_by = db.Column(db.String(80), nullable=False)
    paste_id = db.Column(db.Integer, db.ForeignKey("paste.id"), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader callback."""
    return User.query.get(int(user_id))
