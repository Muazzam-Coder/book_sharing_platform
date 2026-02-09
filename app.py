import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'win11_secret_key_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# --- Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), default='Member')

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    book_type = db.Column(db.String(10)) 
    status = db.Column(db.String(20), default='Available')
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    file_link = db.Column(db.String(200))
    location = db.Column(db.String(100))
    image_url = db.Column(db.String(500))

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    borrower_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='Pending')
    meeting_details = db.Column(db.String(200))
    book = db.relationship('Book', backref='requests')
    borrower = db.relationship('User', backref='my_requests')

# --- Auth Setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---
@app.route('/')
def index():
    return redirect(url_for('browse'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('browse'))
        flash('Invalid Credentials')
    return render_template('login.html', register=False)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form['password'])
        new_user = User(username=request.form['username'], password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('login.html', register=True)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/browse')
@login_required
def browse():
    books = Book.query.all()
    return render_template('browse.html', books=books)

@app.route('/add_book', methods=['POST'])
@login_required
def add_book():
    new_book = Book(
        title=request.form['title'],
        author=request.form['author'],
        category=request.form['category'],
        book_type=request.form['book_type'],
        file_link=request.form.get('file_link'),
        location=request.form.get('location'),
        image_url=request.form.get('image_url'),
        owner_id=current_user.id
    )
    db.session.add(new_book)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/borrow/<int:book_id>', methods=['POST'])
@login_required
def borrow(book_id):
    book = Book.query.get(book_id)
    if book.book_type == 'Digital':
        book.status = 'Borrowed'
        new_req = Request(book_id=book.id, borrower_id=current_user.id, status='Accepted')
        db.session.add(new_req)
    else:
        details = f"Meet at: {request.form['date']} | {request.form['location']}"
        new_req = Request(book_id=book.id, borrower_id=current_user.id, meeting_details=details)
        db.session.add(new_req)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    my_books = Book.query.filter_by(owner_id=current_user.id).all()
    borrowed = Request.query.filter_by(borrower_id=current_user.id).all()
    incoming = Request.query.join(Book).filter(Book.owner_id == current_user.id, Request.status == 'Pending').all()
    return render_template('dashboard.html', my_books=my_books, borrowed=borrowed, incoming=incoming)

@app.route('/action/<int:req_id>/<string:act>')
@login_required
def handle_request(req_id, act):
    req = Request.query.get(req_id)
    if act == 'accept':
        req.status = 'Accepted'
        req.book.status = 'Borrowed'
    elif act == 'return':
        req.status = 'Returned'
        req.book.status = 'Available'
    db.session.commit()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password=generate_password_hash('admin123'), role='Admin')
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)