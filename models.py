from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    books = db.relationship('Book', backref='owner', lazy=True)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    book_type = db.Column(db.String(10)) # 'Physical' or 'Digital'
    status = db.Column(db.String(20), default='Available') # Available, Borrowed
    file_path = db.Column(db.String(200)) # For digital books
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class BorrowRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    borrower_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='Pending') # Pending, Accepted, Rejected, Returned
    # For physical exchange
    proposed_date = db.Column(db.String(50))
    proposed_time = db.Column(db.String(50))
    location = db.Column(db.String(200))