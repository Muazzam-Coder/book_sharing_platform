from flask import Flask, render_template, request, redirect, url_for, flash, abort, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Book, BorrowRequest
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'epub', 'txt'}

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login' # Tells flask where to go if not logged in
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- AUTHENTICATION ROUTES (REQUIRED) ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form.get('password'))
        # Check if first user, make them admin
        is_first = User.query.count() == 0
        new_user = User(username=request.form.get('username'), 
                        email=request.form.get('email'), 
                        password=hashed_pw,
                        is_admin=is_first)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user and check_password_hash(user.password, request.form.get('password')):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash("Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- CORE LOGIC ---

@app.route('/')
def index():
    books = Book.query.filter_by(status='Available').all()
    return render_template('index.html', books=books)

@app.route('/request_borrow/<int:book_id>', methods=['POST'])
@login_required
def request_borrow(book_id):
    book = Book.query.get_or_404(book_id)
    
    if book.status != 'Available':
        flash("Book is already borrowed.")
        return redirect(url_for('index'))

    if book.book_type == 'Digital':
        new_req = BorrowRequest(book_id=book_id, borrower_id=current_user.id, status='Accepted')
        book.status = 'Borrowed'
        db.session.add(new_req)
        db.session.commit()
        flash("Digital book added to your dashboard!")
    else:
        new_req = BorrowRequest(
            book_id=book_id, 
            borrower_id=current_user.id,
            proposed_date=request.form.get('date'),
            proposed_time=request.form.get('time'),
            location=request.form.get('location'),
            status='Pending'
        )
        db.session.add(new_req)
        db.session.commit()
        flash("Request sent to owner!")
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    my_books = Book.query.filter_by(owner_id=current_user.id).all()
    # Logic to see requests people sent to ME
    incoming_requests = BorrowRequest.query.join(Book).filter(Book.owner_id == current_user.id, BorrowRequest.status == 'Pending').all()
    # Logic to see books I AM BORROWING from others
    borrowed_books = BorrowRequest.query.filter_by(borrower_id=current_user.id, status='Accepted').all()
    return render_template('dashboard.html', my_books=my_books, incoming=incoming_requests, borrowed=borrowed_books)

@app.route('/accept_request/<int:request_id>', methods=['POST'])
@login_required
def accept_request(request_id):
    req = BorrowRequest.query.get_or_404(request_id)
    if req.book.owner_id != current_user.id:
        abort(403)
    
    req.status = 'Accepted'
    req.book.status = 'Borrowed'
    db.session.commit()
    flash("Request accepted!")
    return redirect(url_for('dashboard'))

@app.route('/return_book/<int:book_id>', methods=['POST'])
@login_required
def return_book(book_id):
    book = Book.query.get_or_404(book_id)
    book.status = 'Available'
    req = BorrowRequest.query.filter_by(book_id=book_id, status='Accepted').first()
    if req:
        req.status = 'Returned'
    db.session.commit()
    flash("Book marked as returned.")
    return redirect(url_for('dashboard'))

# --- DIGITAL FILE HANDLING ---

@app.route('/download/<int:book_id>')
@login_required
def download_book(book_id):
    book = Book.query.get_or_404(book_id)
    # Only allow download if they have an 'Accepted' borrow request
    req = BorrowRequest.query.filter_by(book_id=book_id, borrower_id=current_user.id, status='Accepted').first()
    if req and book.file_path:
        return send_from_directory(app.config['UPLOAD_FOLDER'], book.file_path)
    abort(403)

# --- ADMIN & UTILS ---

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        book_type = request.form.get('book_type')
        file_path = None

        if book_type == 'Digital':
            file = request.files.get('book_file')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                file_path = filename

        new_book = Book(title=title, author=author, book_type=book_type, file_path=file_path, owner_id=current_user.id)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_book.html')

@app.route('/admin_panel')
@login_required
@admin_required
def admin_panel():
    return render_template('admin.html', books=Book.query.all(), users=User.query.all())

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)