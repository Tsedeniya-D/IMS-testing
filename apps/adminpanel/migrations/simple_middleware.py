from django.shortcuts import redirect
from django.contrib.auth import logout
from django.conf import settings
from django.utils import timezone
import time

class SimpleSessionMiddleware:
    """
    Simple session security middleware without complex logic
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Process the request
        response = self.get_response(request)
        
        # Only apply to admin routes and authenticated users
        if (request.user.is_authenticated and 
            request.path.startswith('/admin/') and 
            request.path != '/admin/login/'):
            
            # Set session expiry on browser close
            if not request.session.get('session_configured'):
                request.session['session_configured'] = True
                request.session.set_expiry(0)  # Expire on browser close
        
        return response
