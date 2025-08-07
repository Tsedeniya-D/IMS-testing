from django.utils import timezone
from django.contrib import admin
from apps.applications.models import InternshipApplication
from apps.departments.models import Department
from matches.models import Match
from approved.models import Approved

admin.site.register(Department)
admin.site.register(InternshipApplication)

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        'get_student_name',
        'get_student_department',
        'get_student_skill',
        'get_department_name',
        'get_department_fields',
        'get_department_skills',
        'get_department_info',
        'status',
    )

    actions = ['approve_selected', 'waitlist_selected', 'reject_selected']

    def get_student_name(self, obj):
        return obj.application.first_name + ' ' + obj.application.last_name
    get_student_name.short_description = 'Student Name'

    def get_student_department(self, obj):
        return obj.application.department
    get_student_department.short_description = 'Student Department'

    def get_student_skill(self, obj):
        return obj.application.skills
    get_student_skill.short_description = 'Student Skill'

    def get_department_name(self, obj):
        return obj.department.department
    get_department_name.short_description = 'Institution Department'

    def get_department_fields(self, obj):
        return obj.department.fields_and_counts
    get_department_fields.short_description = 'Fields and Counts'

    def get_department_skills(self, obj):
        return obj.department.skills
    get_department_skills.short_description = 'Department Skills'

    def get_department_info(self, obj):
        return obj.department.additional_info
    get_department_info.short_description = 'Department Additional Info'

def run_matching_algorithm(self, request, queryset):
    applications = InternshipApplication.objects.filter(status='pending')  # Or your criteria
    departments = Department.objects.all()
    created = 0
    updated = 0

    for dept in departments:
        # Extract all required majors from fields_and_counts
        required_majors = [item['field'].strip().lower() for item in dept.fields_and_counts if 'field' in item]
        for app in applications:
            if not app.department:
                continue
            studentdept = app.department.strip().lower()
            if studentdept in required_majors:
                match, was_created = Match.objects.get_or_create(
                    application=app,
                    department=dept,
                    defaults={
                        'student_name': f"{app.first_name} {app.last_name}",
                        'student_department': app.department,
                        'student_skill': app.skills or '',
                        'institution_department': dept.department,
                        'fields_and_counts': dept.fields_and_counts,
                        'department_skills': dept.skills or '',
                        'department_additional_info': dept.additional_info or '',
                        'status': 'pending',
                        'matched_on': timezone.now(),
                    }
                )
                if not was_created:
                    # If it exists already, update the missing fields
                    match.student_name = f"{app.first_name} {app.last_name}"
                    match.student_department = app.department
                    match.student_skill = app.skills or ''
                    match.institution_department = dept.department
                    match.fields_and_counts = dept.fields_and_counts
                    match.department_skills = dept.skills or ''
                    match.department_additional_info = dept.additional_info or ''
                    match.status = 'pending'
                    match.save()
                    updated += 1
                else:
                    created += 1

    self.message_user(request, f"Matching complete. {created} new matches created. {updated} existing matches updated.")
    run_matching_algorithm.short_description = "Run Matching Algorithm"

    def approve_selected(self, request, queryset):
        for match in queryset:
            match.status = 'approved'
            match.save()
            Approved.objects.get_or_create(match=match)
        self.message_user(request, "Selected matches approved.")
    approve_selected.short_description = "Approve selected"

    def waitlist_selected(self, request, queryset):
        queryset.update(status='waitlist')
        self.message_user(request, "Selected matches waitlisted.")
    waitlist_selected.short_description = "Waitlist selected"

    def reject_selected(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, "Selected matches rejected.")
    reject_selected.short_description = "Reject selected"


@admin.register(Approved)
class ApprovedAdmin(admin.ModelAdmin):
    list_display = ('match', 'approved_on')
