import os

class Config:
    # PocketBase configuration
    POCKETBASE_URL = os.environ.get('POCKETBASE_URL', 'http://127.0.0.1:8090')
    
    # Admin email for admin requests
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'arshtyagi007@gmail.com')
    
    # Categories and subjects
    CATEGORIES = [
        {'id': 'class-9', 'name': 'Class 9', 'image': 'https://images.unsplash.com/photo-1513151233558-d860c5398176'},
        {'id': 'class-10', 'name': 'Class 10', 'image': 'https://images.unsplash.com/photo-1519751138087-5bf79df62d5b'},
        {'id': 'class-11', 'name': 'Class 11', 'image': 'https://images.unsplash.com/photo-1513542789411-b6a5d4f31634'},
        {'id': 'class-12', 'name': 'Class 12', 'image': 'https://images.unsplash.com/photo-1472289065668-ce650ac443d2'},
        {'id': 'jee', 'name': 'JEE', 'image': 'https://images.unsplash.com/photo-1501349800519-48093d60bde0'},
        {'id': 'neet', 'name': 'NEET', 'image': 'https://images.unsplash.com/photo-1487088678257-3a541e6e3922'},
        {'id': 'nda', 'name': 'NDA', 'image': 'https://images.unsplash.com/photo-1493723843671-1d655e66ac1c'}
    ]
    
    SUBJECTS = [
        'Physics', 'Chemistry', 'Biology', 'Mathematics', 
        'English', 'Hindi', 'Social Science', 'Computer Science'
    ]
    
    # App theme colors
    COLORS = {
        'primary': '#4F46E5',  # Indigo-600
        'secondary': '#EC4899',  # Pink-500
        'accent': '#10B981',  # Emerald-500
        'dark': '#1F2937',  # Gray-800
        'light': '#F9FAFB',  # Gray-50
    }
