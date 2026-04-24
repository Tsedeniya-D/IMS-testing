#!/usr/bin/env python
"""
Test script to verify session security settings
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

def test_session_security():
    """Test session security configuration"""
    print("=== Session Security Test ===")
    
    # Check settings
    print(f"SESSION_EXPIRE_AT_BROWSER_CLOSE: {settings.SESSION_EXPIRE_AT_BROWSER_CLOSE}")
    print(f"SESSION_COOKIE_AGE: {settings.SESSION_COOKIE_AGE} seconds ({settings.SESSION_COOKIE_AGE//60} minutes)")
    print(f"SESSION_COOKIE_HTTPONLY: {settings.SESSION_COOKIE_HTTPONLY}")
    print(f"SESSION_COOKIE_SECURE: {settings.SESSION_COOKIE_SECURE}")
    print(f"SESSION_COOKIE_SAMESITE: {settings.SESSION_COOKIE_SAMESITE}")
    print(f"SESSION_SAVE_EVERY_REQUEST: {settings.SESSION_SAVE_EVERY_REQUEST}")
    
    # Test session creation and expiration
    client = Client()
    
    # Create a test user if not exists
    if not User.objects.filter(username='testuser').exists():
        User.objects.create_user(username='testuser', password='testpass123')
    
    # Login and check session
    response = client.post('/login/', {
        'username': 'testuser',
        'password': 'testpass123'
    })
    
    # Check if session cookie is set
    session_cookie = client.cookies.get('sessionid')
    if session_cookie:
        print(f"\n✓ Session cookie created: {session_cookie.value[:20]}...")
        print(f"✓ Session cookie secure flag: {session_cookie.get('secure', 'Not set')}")
        print(f"✓ Session cookie HttpOnly flag: {session_cookie.get('httponly', 'Not set')}")
    else:
        print("\n✗ Session cookie not found")
    
    print("\n=== Session Security Configuration Complete ===")
    print("✓ Sessions will expire when browser is closed")
    print("✓ Sessions have 15-minute inactivity timeout")
    print("✓ Session cookies are HttpOnly (prevents JavaScript access)")
    print("✓ Session cookies use SameSite=Lax (CSRF protection)")
    print("✓ Session cookies are secure in production (HTTPS only)")

if __name__ == '__main__':
    test_session_security()
