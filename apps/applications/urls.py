from django.urls import path
from . import views

urlpatterns = [
    path('', views.apply_internship, name='apply_internship'),
    path('submit/', views.internship_application, name='internship_application'),
    path('test-success/', views.test_success, name='test_success'),
    path('check-email/', views.check_email, name='check_email'),
     path('send-verification/', views.send_verification_code, name='send_verification'),
    path('verify-code/', views.verify_code, name='verify_code'),
    path('test-success/', views.test_success, name='test_success'),
]