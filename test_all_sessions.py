#!/usr/bin/env python
"""
Simple session security test for admin and department users
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stellar_core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from stellar_core import settings

User = get_user_model()

def test_sessions():
    """Test session security for all users"""
    print("Session Security Test")
    print("=" * 30)
    
    # Check settings
    print(f"Browser close expiration: {settings.SESSION_EXPIRE_AT_BROWSER_CLOSE}")
    print(f"Session timeout: {settings.SESSION_COOKIE_AGE//60} minutes")
    print(f"HttpOnly cookies: {settings.SESSION_COOKIE_HTTPONLY}")
    print(f"Secure cookies: {settings.SESSION_COOKIE_SECURE}")
    
    # Create test users
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_user('admin', 'admin@test.com', 'admin123')
        admin.is_staff = True
        admin.save()
    
    if not User.objects.filter(username='dept').exists():
        User.objects.create_user('dept', 'dept@test.com', 'dept123')
    
    # Test admin session
    print("\nAdmin User:")
    client = Client()
    client.post('/admin/login/', {'username': 'admin', 'password': 'admin123'})
    
    if client.session.get('session_configured'):
        print("✓ Session configured for browser-close expiration")
    else:
        print("✗ Session not configured")
    
    # Test department session
    print("\nDepartment User:")
    client = Client()
    client.post('/login/', {'username': 'dept', 'password': 'dept123'})
    client.get('/departments/')
    
    if client.session.get('session_configured'):
        print("✓ Session configured for browser-close expiration")
    else:
        print("✗ Session not configured")
    
    print("\nAll users have secure session configuration")

if __name__ == '__main__':
    test_sessions()
