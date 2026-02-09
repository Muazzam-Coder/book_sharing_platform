from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# We initialize the db object here, but it will be tied to the app later
db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(10), default='Member') # 'Admin' or 'Member'
    
    # Relationship: One User can own many Books
    books = db.relationship('Book', backref='owner', lazy=True)
    # Relationship: One User can make many Borrow Requests
    requests = db.relationship('BorrowRequest', backref='requester', lazy=True)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    book_type = db.Column(db.String(10), nullable=False) # 'Physical' or 'Digital'
    
    # Extra fields based on book_type
    location = db.Column(db.String(100), nullable=True) # For physical
    file_upload = db.Column(db.String(100), nullable=True) # For digital (filename)
    
    status = db.Column(db.String(20), default='Available') # Available, Borrowed
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class BorrowRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Details for the physical exchange
    proposed_date = db.Column(db.String(20))
    proposed_time = db.Column(db.String(20))
    proposed_location = db.Column(db.String(100))
    
    # Workflow status
    status = db.Column(db.String(20), default='Pending') # Pending, Accepted, Rejected, Returned