from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='Member') # Admin or Member
    books = db.relationship('Book', backref='owner', lazy=True)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    book_type = db.Column(db.String(10)) # 'Physical' or 'Digital'
    status = db.Column(db.String(20), default='Available') # Available, Borrowed
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    file_path = db.Column(db.String(200)) # For digital
    location_notes = db.Column(db.Text) # For physical

class BorrowRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    borrower_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='Pending') # Pending, Accepted, Rejected, Returned
    proposed_date = db.Column(db.String(50))
    proposed_location = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)