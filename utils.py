import os
import json
import requests
from flask import flash, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Book
from app import db

# PocketBase API utilities
def pb_login(email, password):
    """Login to PocketBase and return auth token"""
    pb_url = os.environ.get('POCKETBASE_URL', 'http://127.0.0.1:8090')
    
    try:
        response = requests.post(
            f"{pb_url}/api/collections/users/auth-with-password",
            json={"email": email, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'token': data['token'],
                'user_id': data['record']['id'],
                'role': data['record'].get('role', 'user'),
                'email': data['record']['email']
            }
        else:
            return None
    except Exception as e:
        current_app.logger.error(f"PocketBase login error: {str(e)}")
        return None

def pb_register(email, password):
    """Register a new user in PocketBase"""
    pb_url = os.environ.get('POCKETBASE_URL', 'http://127.0.0.1:8090')
    
    try:
        response = requests.post(
            f"{pb_url}/api/collections/users/records",
            json={
                "email": email,
                "password": password,
                "passwordConfirm": password,
                "role": "user",
                "approved": True
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'user_id': data['id'],
                'email': data['email']
            }
        else:
            return None
    except Exception as e:
        current_app.logger.error(f"PocketBase register error: {str(e)}")
        return None

def pb_get_books(category=None, search=None, tag=None):
    """Get books from PocketBase with optional filtering"""
    pb_url = os.environ.get('POCKETBASE_URL', 'http://127.0.0.1:8090')
    
    filter_str = ""
    if category:
        filter_str = f"category='{category}'"
    
    if search:
        search_filter = f"title~'{search}' || author~'{search}'"
        filter_str = f"{filter_str} && {search_filter}" if filter_str else search_filter
    
    if tag:
        tag_filter = f"tags~'{tag}'"
        filter_str = f"{filter_str} && {tag_filter}" if filter_str else tag_filter
    
    params = {'filter': filter_str} if filter_str else {}
    
    try:
        response = requests.get(
            f"{pb_url}/api/collections/books/records",
            params=params
        )
        
        if response.status_code == 200:
            return response.json()['items']
        else:
            return []
    except Exception as e:
        current_app.logger.error(f"PocketBase get books error: {str(e)}")
        return []

def create_local_user(email, password, role='user'):
    """Create a local user in the database"""
    try:
        password_hash = generate_password_hash(password)
        user = User(email=email, password_hash=password_hash, role=role)
        db.session.add(user)
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating local user: {str(e)}")
        return None

def verify_user(email, password):
    """Verify user credentials in local database"""
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None

def user_exists(email):
    """Check if a user exists in the local database"""
    return User.query.filter_by(email=email).first() is not None

def is_admin(user_id):
    """Check if a user is an admin"""
    user = User.query.get(user_id)
    return user and user.role == 'admin'

def get_all_books(category=None, search=None, tag=None):
    """Get books from local database with optional filtering"""
    query = Book.query
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter((Book.title.like(search_term)) | 
                             (Book.author.like(search_term)))
    
    if tag:
        tag_term = f"%{tag}%"
        query = query.filter(Book.tags.like(tag_term))
    
    return query.order_by(Book.created_at.desc()).all()

def increment_download_count(book_id):
    """Increment the download count for a book"""
    book = Book.query.get(book_id)
    if book:
        book.downloads += 1
        db.session.commit()
        return True
    return False
