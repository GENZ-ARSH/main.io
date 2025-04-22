import os
import json
from flask import render_template, request, redirect, url_for, flash, session, jsonify, send_file, current_app
from app import app, db
from models import User, Book, BookRequest, AdminRequest, Announcement
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, SubmitField, HiddenField, validators
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
    announcements = Announcement.query.order_by(Announcement.post_date.desc()).limit(3).all()
    return render_template('index.html', 
                           categories=categories, 
                           featured_books=featured_books,
                           announcements=announcements)

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

@app.route('/announcements')
def announcements():
    announcements_list = Announcement.query.order_by(Announcement.post_date.desc()).all()
    return render_template('announcements.html', announcements=announcements_list)

@app.route('/announcements/<int:announcement_id>')
def announcement_detail(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    return render_template('announcement_detail.html', announcement=announcement)

@app.route('/post-announcement', methods=['GET', 'POST'])
def post_announcement():
    form = AnnouncementForm()
    
    if form.validate_on_submit():
        # Check the secret code
        if form.secret_code.data != 'GENZCLANX':
            flash('Invalid secret code. Access denied.', 'error')
            return render_template('post_announcement.html', form=form)
        
        # Create a new announcement
        announcement = Announcement(
            title=form.title.data,
            description=form.description.data,
            image_url=form.image_url.data if form.image_url.data else None,
            created_by=session.get('email', 'Anonymous')
        )
        
        db.session.add(announcement)
        db.session.commit()
        
        flash('Announcement posted successfully!', 'success')
        return redirect(url_for('announcements'))
    
    return render_template('post_announcement.html', form=form)

@app.route('/delete-announcement/<int:announcement_id>', methods=['POST'])
@admin_required
def delete_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    db.session.delete(announcement)
    db.session.commit()
    
    flash('Announcement deleted successfully', 'success')
    return redirect(url_for('announcements'))

@app.route('/toggle-theme', methods=['POST'])
def toggle_theme():
    current_theme = session.get('theme', 'light')
    new_theme = 'dark' if current_theme == 'light' else 'light'
    session['theme'] = new_theme
    return jsonify({'theme': new_theme})

@app.context_processor
def inject_theme():
    return dict(theme=session.get('theme', 'light'))

# Secure Admin Login Form
class SecureAdminLoginForm(FlaskForm):
    password = PasswordField('Admin Password', [validators.DataRequired()])
    submit = SubmitField('Authenticate')

# Book Edit Form
class BookEditForm(FlaskForm):
    title = StringField('Title', [validators.DataRequired()])
    author = StringField('Author', [validators.DataRequired()])
    category = SelectField('Category', [validators.DataRequired()])
    subject = SelectField('Subject')
    file_url = StringField('File URL', [validators.DataRequired()])
    cover_image = StringField('Cover Image URL')
    file_size = StringField('File Size')
    file_format = SelectField('File Format', choices=[
        ('PDF', 'PDF'), ('EPUB', 'EPUB'), ('MOBI', 'MOBI'), 
        ('DOC', 'DOC'), ('DOCX', 'DOCX'), ('ZIP', 'ZIP')
    ])
    tags = StringField('Tags')
    submit = SubmitField('Save Changes')

# Announcement Form
class AnnouncementForm(FlaskForm):
    title = StringField('Announcement Title', [validators.DataRequired(), validators.Length(min=5, max=200)])
    description = TextAreaField('Description', [validators.DataRequired()])
    image_url = StringField('Image URL (Optional)', [validators.Optional(), validators.URL()])
    secret_code = PasswordField('Secret Code', [validators.DataRequired()]) 
    submit = SubmitField('Post Announcement')

# Secure Admin Access - Enter with password
@app.route('/secure-admin', methods=['GET', 'POST'])
def secure_admin_login():
    form = SecureAdminLoginForm()
    
    if form.validate_on_submit():
        # Check if the admin password matches
        admin_password = os.environ.get('ADMIN_PASSWORD', 'genz-admin-123')  # Default for development
        
        if form.password.data == admin_password:
            session['secure_admin'] = True
            flash('Secure admin access granted', 'success')
            return redirect(url_for('admin_book_management'))
        else:
            flash('Invalid admin password', 'error')
    
    return render_template('admin_login.html', form=form)

# Secure Admin Book Management
@app.route('/secure-admin/books')
def admin_book_management():
    # Check if user has secure admin access
    if not session.get('secure_admin'):
        flash('Secure admin access required', 'error')
        return redirect(url_for('secure_admin_login'))
    
    # Get search, category and sort parameters
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    sort = request.args.get('sort', 'title')
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Books per page
    
    # Start with all books
    query = Book.query
    
    # Apply search filter if provided
    if search:
        query = query.filter(
            (Book.title.ilike(f'%{search}%')) | 
            (Book.author.ilike(f'%{search}%')) |
            (Book.tags.ilike(f'%{search}%'))
        )
    
    # Apply category filter if provided
    if category:
        query = query.filter_by(category=category)
    
    # Apply sorting
    if sort == 'title':
        query = query.order_by(Book.title)
    elif sort == 'author':
        query = query.order_by(Book.author)
    elif sort == 'downloads':
        query = query.order_by(Book.downloads.desc())
    elif sort == 'date':
        query = query.order_by(Book.created_at.desc())
    
    # Paginate results
    pagination = query.paginate(page=page, per_page=per_page)
    books = pagination.items
    
    return render_template('admin_book_management.html', 
                          books=books,
                          pagination=pagination,
                          search=search,
                          category=category,
                          sort=sort,
                          categories=app.config['CATEGORIES'])

# Edit Book
@app.route('/secure-admin/books/<int:book_id>/edit', methods=['GET', 'POST'])
def edit_book(book_id):
    # Check if user has secure admin access
    if not session.get('secure_admin'):
        flash('Secure admin access required', 'error')
        return redirect(url_for('secure_admin_login'))
    
    book = Book.query.get_or_404(book_id)
    form = BookEditForm(obj=book)
    
    # Set up dynamic choices for category and subject
    form.category.choices = [(c['id'], c['name']) for c in app.config['CATEGORIES']]
    form.subject.choices = [(s, s) for s in app.config['SUBJECTS']]
    form.subject.choices.insert(0, ('', '-- Select Subject --'))
    
    if form.validate_on_submit():
        form.populate_obj(book)
        db.session.commit()
        flash('Book updated successfully', 'success')
        return redirect(url_for('admin_book_management'))
    
    return render_template('edit_book.html', 
                          form=form, 
                          book=book,
                          categories=app.config['CATEGORIES'],
                          subjects=app.config['SUBJECTS'])
