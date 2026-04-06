
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import InternshipApplication
from .forms import InternshipApplicationForm
import random
import time
from django.core.mail import send_mail

def apply_internship(request):
    form = InternshipApplicationForm()
    return render(request, 'interns.html', {
        'form': form,
        'status': request.session.get('application_status')
})

def internship_application(request):
    if request.method == 'POST':
        print("POST request received")
    try:
        data = request.POST.copy()
        files = request.FILES.copy()

        # Map camelCase and underscored fields into form field names
        data['first_name'] = data.get('firstname', data.get('firstName', '')).strip()
        data['last_name'] = data.get('lastname', data.get('lastName', '')).strip()
        data['college_name'] = data.get('college_name', data.get('collegeName', '')).strip()
        data['education_level'] = data.get('education_level', data.get('educationLevel', '')).strip()
        is_graduate = data.get('education_level') == 'Graduate'

            # Logic: If they are a graduate, set these to None (Optional) to prevent crashes
        data['current_year'] = data.get('currentYear', '').strip() if not is_graduate else None
        data['expected_graduation'] = data.get('expectedGraduation', '').strip() if not is_graduate else None
        data['start_date'] = data.get('start_date', data.get('startDate', ''))
        data['end_date'] = data.get('end_date', data.get('endDate', ''))
        files['passport_id'] = files.get('passport_id', files.get('passportId', None))
        files['motivation_letter'] = files.get('motivation_letter', files.get('motivationLetter', None))
        files['recommendation_letter'] = files.get('recommendation_letter', files.get('recommendationLetter', None))

        # 1. THE SECURITY CHECK (This protects the SuperAdmin)
        # We pass your data into the form just to check if it's valid
        form = InternshipApplicationForm(data, files)
    except Exception as e:
        print(f"Error processing form data: {e}")
        return JsonResponse({'success': False, 'message': 'Invalid form data. Please check your inputs.'})

            # 2. THE EMAIL VERIFICATION CHECK (This protects the SuperAdmin and the user)   
    if not request.session.get('email_verified') or request.session.get('verification_email') != data.get('email'):
        form.add_error('email', "Please verify your email before submitting.")
    return render(request, 'interns.html', {
    'form': form,
    'status': request.session.get('application_status')
})

    if form.is_valid():
            try:
                application = InternshipApplication.objects.create(
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    age=form.cleaned_data['age'],
                    email=form.cleaned_data['email'],
                    phone=form.cleaned_data['phone'],
                    city=form.cleaned_data['city'],
                    university=form.cleaned_data['university'],
                    college_name=form.cleaned_data['college_name'],
                    nationality=form.cleaned_data['nationality'],
                    address=form.cleaned_data['address'],
                    education_level=form.cleaned_data['education_level'],
                    cgpa=form.cleaned_data['cgpa'],
                    passport_id=form.cleaned_data['passport_id'],
                    department=form.cleaned_data['department'],
                    current_year=form.cleaned_data['current_year'],
                    expected_graduation=form.cleaned_data['expected_graduation'],
                    duration=form.cleaned_data['duration'],
                    start_date=form.cleaned_data['start_date'],
                    end_date=form.cleaned_data['end_date'],
                    skills=form.cleaned_data['skills'],
                    interests=form.cleaned_data['interests'],
                    motivation_letter=form.cleaned_data['motivation_letter'],
                    resume=form.cleaned_data['resume'],
                    recommendation_letter=form.cleaned_data['recommendation_letter'],
                )
                request.session['application_status'] = 'pending'
                return redirect('/applications/success/')
            except Exception as e:
                print(f"Error creating application: {e}")
                return render(request, 'interns.html', {
                    'form': form,
                    'errors': {'general': 'An error occurred while saving your application. Please try again.'},
                    'status': request.session.get('application_status')
                })
            else:
                return render(request, 'interns.html', {
                'form': form,
                'errors': form.errors,
                'status': request.session.get('application_status')
            })

    else:
        # GET or other methods should not submit form; show application page
        return redirect('apply_internship')


def application_success(request):
    return render(request, 'success.html')

# Test-only view to ensure success page is reachable
def test_success(request):
    return render(request, 'success.html')

def check_email(request):
    email = request.GET.get('email', '').strip().lower()
    exists = InternshipApplication.objects.filter(email__iexact=email).exists()
    return JsonResponse({'exists': exists})

def send_verification_code(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'})

    email = request.POST.get('email', '').strip().lower()
    if not email or '@' not in email:
        return JsonResponse({'success': False, 'message': 'Valid email required'})

# Check if email is already registered
    if InternshipApplication.objects.filter(email__iexact=email).exists():
        return JsonResponse({'success': False, 'message': 'Email already registered'})

    # Generate 6-digit code
    code = str(random.randint(100000, 999999))

    # Store in session with expiry (10 minutes)
    request.session['verification_code'] = code
    request.session['verification_email'] = email
    request.session['verification_expiry'] = time.time() + 10*60  # 10 minutes

    try:
        send_mail(
            'Your Internship Verification Code',
            f'Your verification code is: {code}\nIt will expire in 10 minutes.',
            None,  # Uses DEFAULT_FROM_EMAIL from settings
            [email],
            fail_silently=False
        )
    except Exception as e:
        # If email sending fails, print code to console for testing
        print(f"Email send failed: {e}, VERIFICATION CODE FOR {email}: {code}")

    return JsonResponse({'success': True})

def verify_code(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'})

        code = request.POST.get('code', '').strip()
        stored_code = request.session.get('verification_code')
        stored_email = request.session.get('verification_email')
        expiry = request.session.get('verification_expiry')

    if not stored_code or not stored_email:
        return JsonResponse({'success': False, 'message': 'No verification code found. Please request a new one.'})

    # Check expiry
    if time.time() > expiry:
        return JsonResponse({'success': False, 'message': 'Code expired. Please request a new one.'})

    # Check code
    if code == stored_code:
        request.session['email_verified'] = True
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'message': 'Invalid verification code'})
