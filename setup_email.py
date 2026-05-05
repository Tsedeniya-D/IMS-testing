#!/usr/bin/env python
"""
Quick email setup script for development
"""
import os

def setup_email():
    print("Email Setup for SSGI Internship System")
    print("=" * 40)
    
    print("\n1. Create a .env file in the project root")
    print("2. Add your Gmail credentials:")
    print()
    
    email = input("Enter your Gmail address: ").strip()
    password = input("Enter your Gmail App Password (16-digit): ").strip()
    
    if email and password:
        env_content = f"""# Email Configuration
EMAIL_HOST_USER={email}
EMAIL_HOST_PASSWORD={password}
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@ssgiinterns.com
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print(f"\n✅ Email configuration saved to .env file")
        print(f"✅ Email: {email}")
        print("\nNote: Make sure you have 2-Step Verification enabled and created an App Password")
        print("Go to: https://myaccount.google.com/security")
    else:
        print("❌ Email and password are required")

if __name__ == '__main__':
    setup_email()
