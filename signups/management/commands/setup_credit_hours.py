from django.core.management.base import BaseCommand
from signups.models import VolunteerType


class Command(BaseCommand):
    help = 'Set up credit hours for existing volunteer types'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Default credit hours for common volunteer activities
        default_credits = {
            'lawn mowing': 1.0,
            'towel washing': 0.5,
            'cleaning': 1.0,
            'maintenance': 1.5,
            'cooking': 1.0,
            'serving': 0.75,
            'setup': 0.5,
            'cleanup': 0.75,
            'childcare': 1.0,
            'teaching': 1.5,
            'organizing': 1.0,
            'fundraising': 1.0,
        }
        
        volunteer_types = VolunteerType.objects.all()
        
        if not volunteer_types.exists():
            self.stdout.write(
                self.style.WARNING('No volunteer types found. Please create some first.')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'Found {volunteer_types.count()} volunteer type(s):\n')
        )
        
        for vt in volunteer_types:
            current_credits = getattr(vt, 'credit_hours', None)
            
            # Try to find a matching default credit value
            suggested_credits = None
            for key, value in default_credits.items():
                if key.lower() in vt.name.lower():
                    suggested_credits = value
                    break
            
            if suggested_credits is None:
                suggested_credits = 1.0  # Default fallback
            
            self.stdout.write(f'  {vt.name}:')
            self.stdout.write(f'    Current credit hours: {current_credits or "Not set"}')
            self.stdout.write(f'    Suggested credit hours: {suggested_credits}')
            
            if current_credits != suggested_credits:
                if not dry_run:
                    vt.credit_hours = suggested_credits
                    vt.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'    ✅ Updated to {suggested_credits} credit hours')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'    🔄 Would update to {suggested_credits} credit hours (dry run)')
                    )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'    ✅ Already set to {suggested_credits} credit hours')
                )
            self.stdout.write('')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('This was a dry run. Use --dry-run=False to apply changes.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Credit hours have been updated for all volunteer types!')
            )
