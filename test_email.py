#!/usr/bin/env python
"""
Test script to verify email configuration
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stellar_core.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email_config():
    """Test email configuration"""
    print("Email Configuration Test")
    print("=" * 30)
    
    print(f"Email Backend: {settings.EMAIL_BACKEND}")
    print(f"Email Host: {settings.EMAIL_HOST}")
    print(f"Email Port: {settings.EMAIL_PORT}")
    print(f"Email Use TLS: {settings.EMAIL_USE_TLS}")
    print(f"Email User: {settings.EMAIL_HOST_USER}")
    print(f"From Email: {settings.DEFAULT_FROM_EMAIL}")
    
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        print("\n❌ Email credentials not configured!")
        print("Please set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in your .env file")
        return False
    
    try:
        print("\n📧 Sending test email...")
        result = send_mail(
            'SSGI Internship - Test Email',
            'This is a test email to verify email configuration is working.',
            settings.DEFAULT_FROM_EMAIL,
            [settings.EMAIL_HOST_USER],  # Send to yourself for testing
            fail_silently=False,
        )
        
        if result == 1:
            print("✅ Test email sent successfully!")
            return True
        else:
            print(f"❌ Email sending failed. Result: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Email sending failed with error: {str(e)}")
        return False

if __name__ == '__main__':
    test_email_config()
