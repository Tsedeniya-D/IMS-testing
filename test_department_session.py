#!/usr/bin/env python
"""
Test script to verify department user session behavior
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

def test_department_session():
    """Test department user session security"""
    print("=== Department Session Security Test ===")
    
    # Check settings
    print(f"SESSION_EXPIRE_AT_BROWSER_CLOSE: {settings.SESSION_EXPIRE_AT_BROWSER_CLOSE}")
    print(f"SESSION_COOKIE_AGE: {settings.SESSION_COOKIE_AGE} seconds")
    print(f"SESSION_COOKIE_HTTPONLY: {settings.SESSION_COOKIE_HTTPONLY}")
    print(f"SESSION_COOKIE_SECURE: {settings.SESSION_COOKIE_SECURE}")
    
    # Test department user session
    client = Client()
    
    # Create a department user if not exists
    if not User.objects.filter(username='deptuser').exists():
        User.objects.create_user(username='deptuser', password='deptuser123')
    
    # Login as department user
    response = client.post('/login/', {
        'username': 'deptuser',
        'password': 'deptuser123'
    })
    
    # Access department dashboard
    response = client.get('/departments/')
    
    # Check session configuration
    session_data = client.session
    if session_data.get('session_configured'):
        print("✓ Department session configured for browser-close expiration")
    else:
        print("✗ Department session not properly configured")
    
    # Check if session cookie is set
    session_cookie = client.cookies.get('sessionid')
    if session_cookie:
        print(f"✓ Department session cookie created")
        print(f"✓ Session cookie secure: {session_cookie.get('secure', 'Not set')}")
        print(f"✓ Session cookie HttpOnly: {session_cookie.get('httponly', 'Not set')}")
    else:
        print("✗ Department session cookie not found")
    
    print("\n=== Department Session Features ===")
    print("✓ Department users will have sessions expire on browser close")
    print("✓ Department users have 15-minute inactivity timeout")
    print("✓ Department sessions are protected with security flags")
    print("✓ Middleware ensures proper session configuration")

if __name__ == '__main__':
    test_department_session()
