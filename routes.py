import os
import json
from flask import render_template, request, redirect, url_for, flash, session, jsonify, send_file, current_app
from app import app, db
from models import User, Book, BookRequest, AdminRequest
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from utils import (
    pb_login, pb_register, pb_get_books, 
    create_local_user, verify_user, user_exists, 
    is_admin, get_all_books, increment_download_count
)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('login'))
        if not is_admin(session['user_id']):
            flash('Admin access required', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    categories = app.config['CATEGORIES']
    featured_books = Book.query.order_by(Book.downloads.desc()).limit(8).all()
    return render_template('index.html', 
                           categories=categories, 
                           featured_books=featured_books)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Try local authentication first
        user = verify_user(email, password)
        
        # If local auth fails, try PocketBase
        if not user:
            auth_data = pb_login(email, password)
            if auth_data:
                # Create or update local user from PocketBase
                if not user_exists(email):
                    user = create_local_user(email, password, role=auth_data.get('role', 'user'))
                else:
                    user = User.query.filter_by(email=email).first()
                    
                # Store PocketBase token
                session['pb_token'] = auth_data['token']
        
        if user:
            session['user_id'] = user.id
            session['email'] = user.email
            session['role'] = user.role
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        
        if password != confirm:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        if user_exists(email):
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Register in PocketBase
        pb_result = pb_register(email, password)
        
        if pb_result:
            # Create local user
            user = create_local_user(email, password)
            if user:
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
        
        flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@app.route('/books/<category>')
def books(category):
    search = request.args.get('search', '')
    tag = request.args.get('tag', '')
    
    books_list = get_all_books(category, search, tag)
    category_info = next((c for c in app.config['CATEGORIES'] if c['id'] == category), None)
    
    return render_template('books.html', 
                           books=books_list, 
                           category=category_info,
                           search=search,
                           tag=tag,
                           subjects=app.config['SUBJECTS'])

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    related_books = Book.query.filter_by(category=book.category).filter(Book.id != book.id).limit(4).all()
    return render_template('book_detail.html', book=book, related_books=related_books)

@app.route('/download/<int:book_id>')
def download_book(book_id):
    increment_download_count(book_id)
    book = Book.query.get_or_404(book_id)
    # In a real implementation, this would redirect to the PocketBase file URL
    # or serve the file directly from your storage
    return redirect(book.file_url)

@app.route('/request-book', methods=['GET', 'POST'])
@login_required
def request_book():
    if request.method == 'POST':
        book_name = request.form.get('book_name')
        author_name = request.form.get('author_name')
        
        if not book_name:
            flash('Book name is required', 'error')
            return render_template('book_request.html')
        
        book_request = BookRequest(
            book_name=book_name,
            author_name=author_name,
            user_email=session['email']
        )
        
        db.session.add(book_request)
        db.session.commit()
        
        flash('Book request submitted successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('book_request.html')

@app.route('/request-admin', methods=['GET', 'POST'])
@login_required
def request_admin():
    if request.method == 'POST':
        reason = request.form.get('reason')
        
        if not reason:
            flash('Please provide a reason for becoming an admin', 'error')
            return render_template('admin_request.html')
        
        admin_request = AdminRequest(
            email=session['email'],
            reason=reason
        )
        
        db.session.add(admin_request)
        db.session.commit()
        
        flash('Admin request submitted successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('admin_request.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    books = Book.query.order_by(Book.created_at.desc()).all()
    book_requests = BookRequest.query.filter_by(status='pending').all()
    admin_requests = AdminRequest.query.filter_by(status='pending').all()
    
    total_books = Book.query.count()
    total_downloads = db.session.query(db.func.sum(Book.downloads)).scalar() or 0
    
    return render_template('admin_dashboard.html',
                           books=books,
                           book_requests=book_requests,
                           admin_requests=admin_requests,
                           total_books=total_books,
                           total_downloads=total_downloads)

@app.route('/admin/upload-book', methods=['GET', 'POST'])
@admin_required
def upload_book():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        category = request.form.get('category')
        subject = request.form.get('subject')
        tags = request.form.get('tags')
        file_size = request.form.get('file_size')
        file_format = request.form.get('file_format')
        cover_image = request.form.get('cover_image')
        file_url = request.form.get('file_url')
        
        # Basic validation
        if not all([title, author, category, file_url]):
            flash('Please fill all required fields', 'error')
            return render_template('book_upload.html', 
                                   categories=app.config['CATEGORIES'],
                                   subjects=app.config['SUBJECTS'])
        
        # Create new book
        book = Book(
            title=title,
            author=author,
            category=category,
            subject=subject,
            tags=tags,
            file_size=file_size,
            file_format=file_format,
            cover_image=cover_image,
            file_url=file_url
        )
        
        db.session.add(book)
        db.session.commit()
        
        flash('Book uploaded successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('book_upload.html', 
                           categories=app.config['CATEGORIES'],
                           subjects=app.config['SUBJECTS'])

@app.route('/admin/approve-admin-request/<int:request_id>', methods=['POST'])
@admin_required
def approve_admin_request(request_id):
    admin_request = AdminRequest.query.get_or_404(request_id)
    
    # Update request status
    admin_request.status = 'approved'
    
    # Find the user and make them an admin
    user = User.query.filter_by(email=admin_request.email).first()
    if user:
        user.role = 'admin'
    
    db.session.commit()
    
    flash(f'Admin request for {admin_request.email} approved!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject-admin-request/<int:request_id>', methods=['POST'])
@admin_required
def reject_admin_request(request_id):
    admin_request = AdminRequest.query.get_or_404(request_id)
    admin_request.status = 'rejected'
    db.session.commit()
    
    flash(f'Admin request for {admin_request.email} rejected', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-book/<int:book_id>', methods=['POST'])
@admin_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    
    flash('Book deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/toggle-theme', methods=['POST'])
def toggle_theme():
    current_theme = session.get('theme', 'light')
    new_theme = 'dark' if current_theme == 'light' else 'light'
    session['theme'] = new_theme
    return jsonify({'theme': new_theme})

@app.context_processor
def inject_theme():
    return dict(theme=session.get('theme', 'light'))
