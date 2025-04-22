from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    approved = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    cover_image = db.Column(db.String(500))  # URL to cover image
    file_url = db.Column(db.String(500))  # URL to file in PocketBase
    file_size = db.Column(db.String(20))  # e.g., "2.3 MB"
    file_format = db.Column(db.String(10))  # e.g., "PDF"
    tags = db.Column(db.String(200))  # Comma-separated tags
    downloads = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50))  # e.g., 'class-9', 'jee', 'neet'
    class_level = db.Column(db.String(20))  # e.g., '9', '10', 'jee'
    subject = db.Column(db.String(50))  # e.g., 'physics', 'chemistry'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Book {self.title}>'

class BookRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(200), nullable=False)
    author_name = db.Column(db.String(100))
    user_email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<BookRequest {self.book_name}>'

class AdminRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AdminRequest {self.email}>'
