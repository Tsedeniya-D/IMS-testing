from django.contrib import admin
from .models import ProgressView

# apps/progress/admin.py

@admin.register(ProgressView)
class ProgressAdmin(admin.ModelAdmin):
    list_display = (
        "student_name",
        "department_name",
        "approved_on",
        "registered",
        "get_start_date",
        "get_end_date",
        "days_remaining_display",
    )
    readonly_fields = (
        "student_name",
        "department_name",
        "approved_on",
        "registered",
        "get_start_date",
        "get_end_date",
        "days_remaining_display",
    )

    def get_start_date(self, obj):
        return obj.start_date
    get_start_date.short_description = "Start Date"

    def get_end_date(self, obj):
        return obj.end_date
    get_end_date.short_description = "End Date"
    def get_queryset(self, request):
        # Only show registered students
        qs = super().get_queryset(request)
        return qs.filter(registered=True)

    # No adding/editing/deleting from this view
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    def days_remaining_display(self, obj):
        if obj.days_remaining is not None:
            return f"{obj.days_remaining} day{'s' if obj.days_remaining != 1 else ''}"
        return "N/A"
    days_remaining_display.short_description = "Days Remaining"
