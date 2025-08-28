from django.contrib import admin

# Register your models here.
# apps/departments/admin.py
from django.contrib import admin, messages
from django.utils import timezone
from .models import DepartmentPortalConfig, Department
from django.shortcuts import redirect


@admin.register(DepartmentPortalConfig)
class DepartmentPortalConfigAdmin(admin.ModelAdmin):
    list_display = ("is_open", "open_from", "open_until", "status_badge")
    actions = ("open_portal", "close_portal", "open_for_7_days")

    def has_add_permission(self, request):
        # Only allow 1 config
        return not DepartmentPortalConfig.objects.exists()

    def changelist_view(self, request, extra_context=None):
        """Redirect directly to the config edit page."""
        obj = DepartmentPortalConfig.get_solo()
        return redirect(f"{obj.pk}/change/")

    def status_badge(self, obj):
        effective = "OPEN" if obj.is_effectively_open else "CLOSED"
        return effective
    status_badge.short_description = "Effective Status"

    @admin.action(description="Open portal (override window)")
    def open_portal(self, request, queryset):
        cfg = DepartmentPortalConfig.get_solo()
        cfg.is_open = True
        cfg.save()
        self.message_user(request, "Departments portal is now OPEN.", level=messages.SUCCESS)

    @admin.action(description="Close portal immediately")
    def close_portal(self, request, queryset):
        cfg = DepartmentPortalConfig.get_solo()
        cfg.is_open = False
        cfg.save()
        self.message_user(request, "Departments portal is now CLOSED.", level=messages.WARNING)

    @admin.action(description="Open portal for the next 7 days")
    def open_for_7_days(self, request, queryset):
        cfg = DepartmentPortalConfig.get_solo()
        now = timezone.now()
        cfg.is_open = True
        cfg.open_from = now
        cfg.open_until = now + timezone.timedelta(days=7)
        cfg.save()
        self.message_user(request, "Departments portal OPEN for 7 days.", level=messages.SUCCESS)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("department", "contact_person", "email", "phone", "intern_count", "submitted_at")
    search_fields = ("department", "contact_person", "email")
    list_filter = ("submitted_at",)
