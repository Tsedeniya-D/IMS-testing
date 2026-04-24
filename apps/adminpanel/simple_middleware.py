from django.shortcuts import redirect
from django.contrib.auth import logout
from django.conf import settings
from django.utils import timezone
import time

class SimpleSessionMiddleware:
    """
    Session security middleware for browser-close expiration
    Works for all authenticated users (admin, department, etc.)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Process the request
        response = self.get_response(request)
        
        # Apply to all authenticated users except login/home pages
        if request.user.is_authenticated and request.path not in ['/login/', '/', '/admin/login/']:
            
            # Ensure session is configured for browser-close expiration
            if not request.session.get('session_configured'):
                request.session['session_configured'] = True
                request.session.set_expiry(0)  # Expire on browser close
                
                # Track session creation time
                request.session['session_created'] = timezone.now().isoformat()
        
        return response
