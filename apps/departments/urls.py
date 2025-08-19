from django.urls import path
from .views import (
    apply_requirements,
    department_submission,
    department_success,
    DepartmentUpdate,
)

urlpatterns = [
    path('', apply_requirements, name='apply_requirements'),
    path('submit/', department_submission, name='department_submission'),
    path('success/', department_success, name='department_success'),
    path('update/<int:pk>/', DepartmentUpdate.as_view(), name='department_update'),
]