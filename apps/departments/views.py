import json
from django.shortcuts import render, redirect
from .models import Department
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.generic.edit import UpdateView
from .forms import DepartmentForm
from django.contrib.auth.decorators import login_required

from django.utils.decorators import method_decorator
from .decorators import departments_open_required, department_user_required
from .utils import normalize_fields_and_counts

@login_required
@department_user_required
@departments_open_required
def department_submission(request):
    # Ensure session is properly configured for browser-close expiration
    if not request.session.get('session_configured'):
        request.session['session_configured'] = True
        request.session.set_expiry(0)  # Expire on browser close
    
    if request.method == 'POST':
        data = request.POST

        try:
            fields_and_counts = json.loads(data.get('fields_and_counts')) if data.get('fields_and_counts') else []
        except json.JSONDecodeError:
            fields_and_counts = []

        fields_and_counts = normalize_fields_and_counts(fields_and_counts)

        # Validate intern count
        intern_count = int(data.get('internCount') or 0)
        if intern_count < 1:
            return render(request, 'departments.html', {
                'error': 'Intern count must be 1 or above. Negative numbers and 0 are not allowed.',
                'success': request.session.get('department_saved')
            })

        # Create the department entry
        try:
            department = Department.objects.create(
                department=data.get('department'),
                intern_count=intern_count,
                fields_and_counts=fields_and_counts,
                skills=data.get('skills'),
                potential_project=data.get('potential_project'),
                mentor=data.get('mentor')
            )

            request.session['department_saved'] = True
            return redirect('department_success')  # redirect to success page
        except Exception as e:
            return render(request, 'departments.html', {
                'error': str(e),
                'success': request.session.get('department_saved')
            })

    # GET request (first page load)
    return render(request, 'departments.html', {
        'success': request.session.get('department_saved')
    })

def department_success(request):
    return render(request, 'depsuccess.html')

def department_change_password(request):
    return render(request, 'departments/department_change_password.html')

@login_required
@department_user_required
@departments_open_required
def apply_requirements(request):
    return render(request, 'departments.html')

@csrf_exempt
def department_update(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        submission_id = data.get('id')
        try:
            department = Department.objects.get(id=submission_id)
            
            # Validate intern count
            intern_count = int(data.get('internCount') or 0)
            if intern_count < 1:
                return JsonResponse({'success': False, 'error': 'Intern count must be 1 or above. Negative numbers and 0 are not allowed.'})
            
            department.department = data.get('department')
            department.intern_count = intern_count
            department.fields_and_counts = normalize_fields_and_counts(data.get('fields'))
            department.skills = data.get('skills')
            department.potential_project = data.get('potential_project')
            department.mentor = data.get('mentor')
            department.save()
            return JsonResponse({'success': True})
        except Department.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Submission not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@method_decorator(login_required, name='dispatch')
@method_decorator(department_user_required, name='dispatch')
@method_decorator(departments_open_required, name='dispatch')
class DepartmentUpdate(UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'departments.html'  # Use your actual template path
    success_url = '/departments/'       # Redirect after successful update

# class DepartmentLoginView(LoginView):
#     template_name = 'dep_login.html'

# @login_required(login_url='/departments/login/')
# def department_requirements(request):
#     return render(request, 'departments.html')
