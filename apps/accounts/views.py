from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from apps.departments.models import Department


# Create your views here.

def home(request):
    return render(request, 'home.html')

def interns(request):
    return render(request, 'interns.html')

@login_required
def departments(request):
    return render(request, 'departments.html')

def department_login(request):
    """Department login - always goes to department dashboard"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Always go to department dashboard regardless of user role
            return redirect('/departments/')
        else:
            return render(request, 'registration/login.html', {
                'error': 'Invalid username or password'
            })
    
    return render(request, 'registration/login.html')


# from django.shortcuts import render
# from apps.departments.models import Department
# from apps.applications.models import InternshipApplication
# from django.contrib.auth.decorators import login_required, user_passes_test

# # Optional: only allow superusers (admins)
# def is_admin(user):
#     return user.is_superuser

# @login_required
# @user_passes_test(is_admin)  # Optional restriction to admin users only
# def home(request):
#     departments = Department.objects.all()
#     applications = InternshipApplication.objects.all()
#     return render(request, 'admin.html', {
#         'departments': departments,
#         'applications': applications
#     })
