from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(10), default='Member') # Admin or Member
    books = db.relationship('Book', backref='owner', lazy=True)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    book_type = db.Column(db.String(10), nullable=False) # Physical or Digital
    status = db.Column(db.String(20), default='Available') # Available, Borrowed
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class BorrowRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Pending') # Pending, Accepted, Rejected