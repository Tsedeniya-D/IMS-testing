from django.shortcuts import render, redirect
from django.http import JsonResponse
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

    # HARD LOCK (prevents duplicate execution instantly)
    lock_key = f"email_lock_{email}"
    last_request_time = request.session.get(lock_key)

    if last_request_time and now - float(last_request_time) < 3:
        return JsonResponse({'success': False, 'message': 'Please wait...'})

    request.session[lock_key] = now

    # ❗ Prevent overwriting existing valid code
    existing_email = request.session.get('verification_email')
    expiry = request.session.get('verification_expiry')

    if existing_email == email and expiry and now < float(expiry):
        return JsonResponse({'success': False, 'message': 'Code already sent. Check your email.'})

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
        send_mail(
            'Your Internship Verification Code',
            f'Your verification code is: {code}\nExpires in 5 minutes.',
            None,
            [email],
            fail_silently=False
        )

        return JsonResponse({'success': True})

    except Exception as e:
        print("MAIL ERROR:", e)
        return JsonResponse({'success': False, 'message': 'Mail server error'})

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
        return JsonResponse({'success': False, 'message': 'No code found.'})

    if email != stored_email:
        return JsonResponse({'success': False, 'message': 'Email mismatch.'})

    if timezone.now().timestamp() > float(expiry):
        return JsonResponse({'success': False, 'message': 'Code expired.'})

    input_hash = salted_hmac('email_verification_code', code).hexdigest()

    if constant_time_compare(input_hash, stored_code_hash):
        request.session['email_verified_email'] = stored_email
        request.session['email_verified_until'] = (timezone.now() + timedelta(minutes=10)).timestamp()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'message': 'Incorrect code.'})