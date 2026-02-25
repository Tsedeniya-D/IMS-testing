from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.applications.models import InternshipApplication
from apps.departments.models import Department
from matches.models import Match

@receiver(post_save, sender=InternshipApplication)
def auto_match_intern(sender, instance, created, **kwargs):
    if not created:
        return

    student_major = instance.department
    if not student_major:
        return

    student_major_lower = student_major.strip().lower()
    matching_depts = []
    all_departments = Department.objects.all()

    for dept in all_departments:
        fields_and_counts = dept.fields_and_counts
        if isinstance(fields_and_counts, dict):
            fields_and_counts = [fields_and_counts]
        elif not isinstance(fields_and_counts, list):
            fields_and_counts = []

        required_fields = {}
        for item in fields_and_counts:
            if not isinstance(item, dict):
                continue
            field_name = item.get('field')
            count_value = item.get('count')
            if not field_name:
                continue
            try:
                count_value = int(count_value)
            except (TypeError, ValueError):
                continue

            required_fields[field_name.strip().lower()] = count_value

        if student_major_lower in required_fields:
            matching_depts.append((dept, required_fields[student_major_lower]))

    if not matching_depts:
        print("❌ No matching department found for this intern.")
        return

    available_depts = []
    for dept, field_capacity in matching_depts:
        current_field_count = Match.objects.filter(
            department=dept,
            status__in=['pending', 'approved'],
            student_department__iexact=student_major.strip()
        ).count()

        print(f"Dept: {dept.department}, Field: {student_major.strip()}, Capacity: {field_capacity}, Current count: {current_field_count}")

        if current_field_count < field_capacity:
            available_depts.append((dept, current_field_count))

    if available_depts:
        dept = sorted(available_depts, key=lambda x: x[1])[0][0]
        status = 'pending'
    else:
        dept = matching_depts[0][0]
        status = 'waitlist'

    match, was_created = Match.objects.get_or_create(
        application=instance,
        department=dept,
        defaults={
            'status': status,
            'student_department': student_major.strip()
        }
    )

    if not was_created and match.status != status:
        match.status = status
        match.save()

    if was_created:
        print(f"✅ Match created: {match} with status {status}")
