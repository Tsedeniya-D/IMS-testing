from django.urls import path
from .views import home, interns, departments, department_login

urlpatterns = [
    path('interns/', interns, name='interns'),
    path('departments/', departments, name='departments'),
    path('login/', department_login, name='department_login'),
    path('', home, name='home'),
]

