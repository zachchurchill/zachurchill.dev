from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
from signups.models import VolunteerForm, VolunteerSlot, VolunteerType, Family

class Command(BaseCommand):
    help = 'Create test data for the volunteer signup system'

    def handle(self, *args, **options):
        # Get an existing superuser or prompt to create one
        superusers = User.objects.filter(is_superuser=True)
        
        if superusers.exists():
            # Use the first superuser found
            user = superusers.first()
            self.stdout.write(f'Using existing superuser: {user.username} ({user.email})')
        else:
            # No superuser exists, prompt to create one
            self.stdout.write(self.style.WARNING('No superuser found. Please create one first using:'))
            self.stdout.write('python manage.py createsuperuser')
            self.stdout.write('Then run this command again.')
            return

        # Create volunteer types
        volunteer_types = [
            {
                'name': 'Lawn Mowing',
                'description': 'Mow the school lawn and trim edges. Equipment provided.',
            },
            {
                'name': 'Trash Duty',
                'description': 'Empty all trash cans and take to dumpster. Replace liners.',
            },
            {
                'name': 'Towel Washing',
                'description': 'Take home school towels to wash and return clean.',
            },
            {
                'name': 'Classroom Helper',
                'description': 'Assist teachers with classroom activities and preparation.',
            },
            {
                'name': 'Event Setup',
                'description': 'Help set up for school events, parties, or special activities.',
            },
            {
                'name': 'Maintenance',
                'description': 'General maintenance tasks around the school building and grounds.',
            },
        ]

        for type_data in volunteer_types:
            volunteer_type, created = VolunteerType.objects.get_or_create(
                name=type_data['name'],
                defaults=type_data
            )
            if created:
                self.stdout.write(f'Created volunteer type: {volunteer_type.name}')

        # Create sample families
        families_data = [
            {
                'last_name': 'Smith',
                'email': 'smith@example.com',
            },
            {
                'last_name': 'Johnson',
                'email': 'johnson@example.com',
            },
            {
                'last_name': 'Williams',
                'email': 'williams@example.com',
            },
            {
                'last_name': 'Brown',
                'email': 'brown@example.com',
            },
            {
                'last_name': 'Davis',
                'email': 'davis@example.com',
            },
        ]

        for family_data in families_data:
            family, created = Family.objects.get_or_create(
                last_name=family_data['last_name'],
                defaults=family_data
            )
            if created:
                self.stdout.write(f'Created family: {family.last_name}')

        # Create the main volunteer form
        form, created = VolunteerForm.objects.get_or_create(
            title='September 2024 Parent Co-op Volunteer Opportunities',
            defaults={
                'description': 'Help keep our school running smoothly! We need volunteers for various tasks throughout September. Please sign up for any slots that work with your schedule.',
                'created_by': user,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created volunteer form: {form.title}'))
            self.stdout.write(f'Form URL: {form.unique_url}')
        else:
            self.stdout.write(self.style.WARNING(f'Form already exists: {form.title}'))

        # Create volunteer slots
        slots_data = [
            # Mowing slots
            {
                'title': 'Lawn Mowing - Week 1',
                'description': 'Mow the school lawn and trim edges. Equipment provided.',
                'date': date(2024, 9, 7),
                'max_volunteers': 2
            },
            {
                'title': 'Lawn Mowing - Week 3',
                'description': 'Mow the school lawn and trim edges. Equipment provided.',
                'date': date(2024, 9, 21),
                'max_volunteers': 2
            },
            # Trash duty slots
            {
                'title': 'Trash Duty - Week 1',
                'description': 'Empty all trash cans and take to dumpster. Replace liners.',
                'date': date(2024, 9, 2),
                'max_volunteers': 1
            },
            {
                'title': 'Trash Duty - Week 2',
                'description': 'Empty all trash cans and take to dumpster. Replace liners.',
                'date': date(2024, 9, 9),
                'max_volunteers': 1
            },
            {
                'title': 'Trash Duty - Week 3',
                'description': 'Empty all trash cans and take to dumpster. Replace liners.',
                'date': date(2024, 9, 16),
                'max_volunteers': 1
            },
            {
                'title': 'Trash Duty - Week 4',
                'description': 'Empty all trash cans and take to dumpster. Replace liners.',
                'date': date(2024, 9, 23),
                'max_volunteers': 1
            },
            {
                'title': 'Trash Duty - Week 5',
                'description': 'Empty all trash cans and take to dumpster. Replace liners.',
                'date': date(2024, 9, 30),
                'max_volunteers': 1
            },
            # Towel washing slots
            {
                'title': 'Towel Washing - Mid Month',
                'description': 'Take home school towels to wash and return clean.',
                'date': date(2024, 9, 15),
                'max_volunteers': 1
            },
            {
                'title': 'Towel Washing - End of Month',
                'description': 'Take home school towels to wash and return clean.',
                'date': date(2024, 9, 30),
                'max_volunteers': 1
            }
        ]

        created_slots = 0
        for slot_data in slots_data:
            slot, created = VolunteerSlot.objects.get_or_create(
                form=form,
                title=slot_data['title'],
                date=slot_data['date'],
                defaults=slot_data
            )
            if created:
                created_slots += 1
                self.stdout.write(f'Created slot: {slot.title}')

        self.stdout.write(self.style.SUCCESS(f'Created {created_slots} new volunteer slots'))
        self.stdout.write(self.style.SUCCESS('Test data creation completed!'))
        self.stdout.write(f'You can view the form at: http://127.0.0.1:8000/form/{form.unique_url}/')
