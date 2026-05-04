from django.shortcuts import redirect
from django.contrib.auth import logout
from django.utils import timezone


class CombinedSessionMiddleware:
    """
    Combines:
    - Role separation (admin vs department)
    - Session expiration (browser close)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # ✅ Allow login pages (avoid infinite loop)
        if path.startswith('/admin/login/') or path.startswith('/login/'):
            return self.get_response(request)

        if request.user.is_authenticated:

            # ✅ Configure session (only once)
            if not request.session.get('session_configured'):
                request.session['session_configured'] = True
                request.session.set_expiry(1800)
                request.session['last_activity'] = timezone.now().timestamp()
                # Session will expire when browser closes due to SESSION_EXPIRE_AT_BROWSER_CLOSE = True
                request.session['session_created'] = timezone.now().isoformat()

            # ✅ Role control
            current_role = self.get_current_role(request)
            requested_role = self.get_requested_role(path)

            if current_role and requested_role and current_role != requested_role:
                logout(request)

                if requested_role == 'admin':
                    return redirect('/admin/login/')
                else:
                    return redirect('/login/')

        return self.get_response(request)

    def get_current_role(self, request):
        if 'admin_session' in request.session:
            return 'admin'
        elif 'department_session' in request.session:
            return 'department'
        return None

    def get_requested_role(self, path):
        if path.startswith('/admin/') and path != '/admin/login/':
            return 'admin'
        elif path.startswith('/departments/'):
            return 'department'
        return None


# ✅ Helper functions

def create_role_session(request, role):
    request.session.pop('admin_session', None)
    request.session.pop('department_session', None)

    if role == 'admin':
        request.session['admin_session'] = {
            'user_id': request.user.id,
            'login_time': timezone.now().isoformat(),
        }

    elif role == 'department':
        request.session['department_session'] = {
            'user_id': request.user.id,
            'login_time': timezone.now().isoformat(),
        }

    request.session.modified = True


def clear_role_sessions(request):
    request.session.pop('admin_session', None)
    request.session.pop('department_session', None)
    request.session.modified = True