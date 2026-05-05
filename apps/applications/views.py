from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from .models import InternshipApplication
from .forms import InternshipApplicationForm
import random
from django.utils import timezone
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.crypto import salted_hmac, constant_time_compare
from datetime import timedelta


# PAGE LOAD
def apply_internship(request):
    form = InternshipApplicationForm()
    return render(request, 'interns.html', {
        'form': form,
        'status': request.session.get('application_status')
    })


  # SUBMIT APPLICATION

def internship_application(request):
    if request.method != 'POST':
        return redirect('apply_internship')

    data = request.POST.copy()
    files = request.FILES.copy()

    data['first_name'] = data.get('firstname', data.get('firstName', '')).strip()
    data['last_name'] = data.get('lastname', data.get('lastName', '')).strip()
    data['college_name'] = data.get('college_name', data.get('collegeName', '')).strip()
    data['education_level'] = data.get('education_level', data.get('educationLevel', '')).strip()

    is_graduate = data.get('education_level') == 'Graduate'
    data['current_year'] = data.get('currentYear', '').strip() if not is_graduate else ''
    data['expected_graduation'] = data.get('expectedGraduation', '').strip() if not is_graduate else ''

    data['start_date'] = data.get('start_date', data.get('startDate', ''))
    data['end_date'] = data.get('end_date', data.get('endDate', ''))

    files['passport_id'] = files.get('passport_id', files.get('passportId', None))
    files['motivation_letter'] = files.get('motivation_letter', files.get('motivationLetter', None))
    files['recommendation_letter'] = files.get('recommendation_letter', files.get('recommendationLetter', None))

    form = InternshipApplicationForm(data, files)

    submitted_email = data.get('email', '').strip().lower()

    verified_email = request.session.get('email_verified_email')
    verified_until = request.session.get('email_verified_until')

    verification_valid = bool(
        verified_email
        and verified_until
        and verified_email == submitted_email
        and timezone.now().timestamp() < float(verified_until)
    )

    if not verification_valid:
        form.add_error('email', "Please verify your email before submitting.")

    if not form.is_valid():
        return render(request, 'interns.html', {
            'form': form,
            'status': request.session.get('application_status')
        })

    existing_application = InternshipApplication.objects.filter(
        email__iexact=submitted_email,
        first_name=data.get('firstname', '').strip(),
        last_name=data.get('lastname', '').strip()
    ).first()

    if existing_application:
        return render(request, 'interns.html', {
            'form': form,
            'status': 'already_submitted',
            'error': 'Application already submitted for this email.'
        })

    form.save()
    request.session['application_status'] = 'pending'

    # Clear verification session
    for key in [
        'verification_code_hash',
        'verification_email',
        'verification_expiry',
        'email_verified_email',
        'email_verified_until',
        'email_lock'
    ]:
        request.session.pop(key, None)

    return redirect('application_success')

# SUCCESS PAGE

def test_success(request):
      return render(request, 'success.html');
    


  # EMAIL CHECK

def check_email(request):
    email = request.GET.get('email', '').strip().lower()
    exists = InternshipApplication.objects.filter(email__iexact=email).exists()
    return JsonResponse({'exists': exists})


  # SEND VERIFICATION CODE (ONLY ONCE)

def send_verification_code(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'})

    email = request.POST.get('email', '').strip().lower()

    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({'success': False, 'message': 'Valid email required'})

    now = timezone.now().timestamp()

    # Check if there's already a valid code for this email
    existing_email = request.session.get('verification_email')
    expiry = request.session.get('verification_expiry')

    # Prevent sending new code if current one is still valid
    if existing_email == email and expiry and now < float(expiry):
        remaining_time = int(float(expiry) - now)
        return JsonResponse({'success': False, 'message': f'Verification code already sent. Please wait {remaining_time//60} minutes and try again.'})

    # Rate limiting - prevent spam
    lock_key = f"email_lock_{email}"
    last_request_time = request.session.get(lock_key)

    if last_request_time and now - float(last_request_time) < 3:
        return JsonResponse({'success': False, 'message': 'Please wait before requesting another code.'})

    request.session[lock_key] = now

    # Generate code
    code = str(random.randint(100000, 999999))
    code_hash = salted_hmac('email_verification_code', code).hexdigest()
    expiry_time = timezone.now() + timedelta(minutes=5)

    # Save session
    request.session['verification_code_hash'] = code_hash
    request.session['verification_email'] = email
    request.session['verification_expiry'] = expiry_time.timestamp()

    # Remove previous verification
    request.session.pop('email_verified_email', None)
    request.session.pop('email_verified_until', None)

    try:
        # Debug: Print email configuration
        print(f"Email Configuration: Backend={settings.EMAIL_BACKEND}, Host={settings.EMAIL_HOST}, Port={settings.EMAIL_PORT}")
        print(f"Email User: {settings.EMAIL_HOST_USER}")
        print(f"Attempting to send verification code to: {email}")
        print(f"Verification code: {code}")  # Show code for debugging
        
        # Check if we have credentials for SMTP
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            print("Email credentials not configured! Please set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env")
            return JsonResponse({'success': False, 'message': 'Email service not configured. Please contact administrator.'})
        
        # Send email to applicant's address
        print(f"Sending verification code to applicant's email: {email}")
        result = send_mail(
            'SSGI Internship - Email Verification Code',
            f'Your verification code is: {code}\n\nThis code will expire in 5 minutes.\n\nIf you did not request this code, please ignore this email.',
            settings.DEFAULT_FROM_EMAIL,
            [email],  # Send to applicant's email
            fail_silently=False
        )
        
        print(f"Email sent successfully to {email}. Result: {result}")
        return JsonResponse({'success': True, 'message': 'Verification code sent to your email'})

    except Exception as e:
        error_msg = str(e)
        print(f"MAIL ERROR: {error_msg}")
        
        # Provide specific error messages
        if "10060" in error_msg or "connection attempt failed" in error_msg.lower():
            return JsonResponse({'success': False, 'message': 'Cannot connect to email server. Please check your internet connection and email configuration.'})
        elif "11001" in error_msg or "getaddrinfo failed" in error_msg.lower():
            return JsonResponse({'success': False, 'message': 'DNS resolution failed. Cannot find email server. Please check your email configuration.'})
        elif "Authentication" in error_msg or "credentials" in error_msg.lower():
            return JsonResponse({'success': False, 'message': 'Email authentication failed. Please check email username and password.'})
        elif "timeout" in error_msg.lower():
            return JsonResponse({'success': False, 'message': 'Email server timeout. Please try again.'})
        else:
            return JsonResponse({'success': False, 'message': f'Email sending failed: {error_msg}'})

    # VERIFY CODE

def verify_code(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'})

    code = request.POST.get('code', '').strip()
    email = request.POST.get('email', '').strip().lower()

    stored_code_hash = request.session.get('verification_code_hash')
    stored_email = request.session.get('verification_email')
    expiry = request.session.get('verification_expiry')

    if not stored_code_hash or not stored_email:
        return JsonResponse({'success': False, 'message': 'No code found. Please request a new code.'})

    if email != stored_email:
        return JsonResponse({'success': False, 'message': 'Email mismatch. Please use the correct email.'})

    if timezone.now().timestamp() > float(expiry):
        # Clear expired code so user can request a new one
        request.session.pop('verification_code_hash', None)
        request.session.pop('verification_email', None)
        request.session.pop('verification_expiry', None)
        return JsonResponse({'success': False, 'message': 'Code expired. Please request a new code.'})

    input_hash = salted_hmac('email_verification_code', code).hexdigest()

    if constant_time_compare(input_hash, stored_code_hash):
        # Clear verification data after successful verification
        request.session['email_verified_email'] = stored_email
        request.session['email_verified_until'] = (timezone.now() + timedelta(minutes=10)).timestamp()
        request.session.pop('verification_code_hash', None)
        request.session.pop('verification_email', None)
        request.session.pop('verification_expiry', None)
        return JsonResponse({'success': True, 'message': 'Email verified successfully!'})

    return JsonResponse({'success': False, 'message': 'Incorrect code. Please try again.'})