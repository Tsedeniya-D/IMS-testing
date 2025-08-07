# applications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.applications.models import InternshipApplication
from apps.departments.models import Department
from matches.models import Match

@receiver(post_save, sender=InternshipApplication)
def auto_match_intern(sender, instance, created, **kwargs):
    print("Signal triggered for:", instance)

    if not created:
        return

    student_major = instance.department
    print("Student's department:", student_major)

    if not student_major:
        return
    
    matching_depts = []
    all_departments = Department.objects.all()

    for dept in all_departments:
        required_fields = [item['field'].strip().lower() for item in dept.fields_and_counts if 'field' in item]
        if student_major.strip().lower() in required_fields:
            matching_depts.append(dept)

    if matching_depts:
        # Match to the department with fewest interns assigned
        dept = sorted(matching_depts, key=lambda d: d.matched_applications.count())[0]

        # Avoid duplicate match
        match, created = Match.objects.get_or_create(
            application=instance,
            department=dept,
            defaults={'status': 'pending'}
        )

        if created:
            print(f"✅ Match created: {match}")
    else:
        print("❌ No matching department found for this intern.")

   