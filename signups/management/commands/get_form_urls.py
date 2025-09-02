from django.core.management.base import BaseCommand
from signups.models import VolunteerForm


class Command(BaseCommand):
    help = 'Get URLs for all volunteer forms'

    def add_arguments(self, parser):
        parser.add_argument(
            '--active-only',
            action='store_true',
            help='Show only active forms',
        )
        parser.add_argument(
            '--form-id',
            type=int,
            help='Show URL for specific form ID',
        )

    def handle(self, *args, **options):
        if options['form_id']:
            try:
                form = VolunteerForm.objects.get(id=options['form_id'])
                self.display_form(form)
            except VolunteerForm.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Form with ID {options["form_id"]} not found')
                )
        else:
            queryset = VolunteerForm.objects.all()
            if options['active_only']:
                queryset = queryset.filter(is_active=True)
            
            if not queryset.exists():
                self.stdout.write(
                    self.style.WARNING('No volunteer forms found')
                )
                return
            
            self.stdout.write(
                self.style.SUCCESS(f'Found {queryset.count()} volunteer form(s):\n')
            )
            
            for form in queryset:
                self.display_form(form)
                self.stdout.write('')  # Empty line for spacing

    def display_form(self, form):
        """Display information about a single form"""
        status = '✅ ACTIVE' if form.is_active else '❌ INACTIVE'
        self.stdout.write(
            f'{status} - {form.title} (ID: {form.id})'
        )
        self.stdout.write(f'  Unique URL: {form.unique_url}')
        self.stdout.write(f'  Full URL: {form.get_form_url()}')
        self.stdout.write(f'  Created: {form.created_at.strftime("%Y-%m-%d %H:%M")}')
        self.stdout.write(f'  Created by: {form.created_by.username}')
