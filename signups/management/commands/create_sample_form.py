from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
from signups.models import VolunteerForm, VolunteerSlot, VolunteerType

class Command(BaseCommand):
    help = 'Create a sample volunteer form with URL "sample-form-for-volunteers"'

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

        # Create volunteer types if they don't exist
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

        # Create the sample volunteer form with specific URL
        form, created = VolunteerForm.objects.get_or_create(
            unique_url='sample-form-for-volunteers',
            defaults={
                'title': 'Sample Volunteer Opportunities',
                'description': 'This is a sample volunteer form to demonstrate the system. Please sign up for any slots that work with your schedule.',
                'created_by': user,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created sample volunteer form: {form.title}'))
            self.stdout.write(f'Form URL: {form.unique_url}')
        else:
            # Update existing form
            form.title = 'Sample Volunteer Opportunities'
            form.description = 'This is a sample volunteer form to demonstrate the system. Please sign up for any slots that work with your schedule.'
            form.is_active = True
            form.save()
            self.stdout.write(self.style.WARNING(f'Updated existing form: {form.title}'))

        # Create volunteer slots
        slots_data = [
            # Mowing slots
            {
                'title': 'Lawn Mowing - Week 1',
                'description': 'Mow the school lawn and trim edges. Equipment provided.',
                'date': date(2024, 9, 7),
                'max_volunteers': 2,
                'volunteer_type': 'Lawn Mowing'
            },
            {
                'title': 'Lawn Mowing - Week 3',
                'description': 'Mow the school lawn and trim edges. Equipment provided.',
                'date': date(2024, 9, 21),
                'max_volunteers': 2,
                'volunteer_type': 'Lawn Mowing'
            },
            # Trash duty slots
            {
                'title': 'Trash Duty - Week 1',
                'description': 'Empty all trash cans and take to dumpster. Replace liners.',
                'date': date(2024, 9, 2),
                'max_volunteers': 1,
                'volunteer_type': 'Trash Duty'
            },
            {
                'title': 'Trash Duty - Week 2',
                'description': 'Empty all trash cans and take to dumpster. Replace liners.',
                'date': date(2024, 9, 9),
                'max_volunteers': 1,
                'volunteer_type': 'Trash Duty'
            },
            {
                'title': 'Trash Duty - Week 3',
                'description': 'Empty all trash cans and take to dumpster. Replace liners.',
                'date': date(2024, 9, 16),
                'max_volunteers': 1,
                'volunteer_type': 'Trash Duty'
            },
            {
                'title': 'Trash Duty - Week 4',
                'description': 'Empty all trash cans and take to dumpster. Replace liners.',
                'date': date(2024, 9, 23),
                'max_volunteers': 1,
                'volunteer_type': 'Trash Duty'
            },
            {
                'title': 'Trash Duty - Week 5',
                'description': 'Empty all trash cans and take to dumpster. Replace liners.',
                'date': date(2024, 9, 30),
                'max_volunteers': 1,
                'volunteer_type': 'Trash Duty'
            },
            # Towel washing slots
            {
                'title': 'Towel Washing - Mid Month',
                'description': 'Take home school towels to wash and return clean.',
                'date': date(2024, 9, 15),
                'max_volunteers': 1,
                'volunteer_type': 'Towel Washing'
            },
            {
                'title': 'Towel Washing - End of Month',
                'description': 'Take home school towels to wash and return clean.',
                'date': date(2024, 9, 30),
                'max_volunteers': 1,
                'volunteer_type': 'Towel Washing'
            }
        ]

        created_slots = 0
        for slot_data in slots_data:
            # Get the volunteer type
            volunteer_type = VolunteerType.objects.get(name=slot_data['volunteer_type'])
            
            slot, created = VolunteerSlot.objects.get_or_create(
                form=form,
                title=slot_data['title'],
                date=slot_data['date'],
                defaults={
                    'description': slot_data['description'],
                    'max_volunteers': slot_data['max_volunteers'],
                    'volunteer_type': volunteer_type
                }
            )
            
            if created:
                created_slots += 1
                self.stdout.write(f'Created slot: {slot.title}')

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_slots} volunteer slots'))
        self.stdout.write(self.style.SUCCESS(f'Sample form is available at: /signups/form/sample-form-for-volunteers/'))
