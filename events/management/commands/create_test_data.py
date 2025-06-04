from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import Event, Registration, EventField, RegistrationFormFieldData
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Create test data for the event registration system'

    def handle(self, *args, **options):
        # Create or get superuser
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))        # Create test event
        event, created = Event.objects.get_or_create(
            name="Tech Conference 2025",
            defaults={
                'description': 'A comprehensive technology conference featuring the latest trends in AI, web development, and cloud computing.',
                'organizer': user,
                'location': 'Tech Center, San Francisco',
                'start_date': datetime.now() + timedelta(days=30),
                'end_date': datetime.now() + timedelta(days=32),
                'start_time': datetime.now().time(),
                'end_time': datetime.now().time(),
                'is_published': True,            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created event: {event.name}'))

        # Create custom fields for the event
        if EventField.objects.filter(event=event).count() == 0:
            fields = [
                {'field_name': 'company', 'field_type': 'text', 'placeholder': 'Company/Organization', 'is_required': False},
                {'field_name': 'experience', 'field_type': 'radio', 'is_required': True, 
                 'choices': 'Beginner\nIntermediate\nAdvanced'},
                {'field_name': 'dietary_requirements', 'field_type': 'textarea', 'placeholder': 'Any dietary requirements?', 'is_required': False},
            ]
            
            for i, field_data in enumerate(fields):
                EventField.objects.create(event=event, order=i, **field_data)            
            self.stdout.write(self.style.SUCCESS('Created custom fields'))

        # Create test registrations
        if Registration.objects.filter(event=event).count() == 0:
            registrations_data = [
                {
                    'participant_name': 'John Doe',
                    'participant_email': 'john.doe@example.com',
                    'participant_phone': '+1-555-0123',
                    'status': 'pending',
                    'field_data': {
                        'company': 'Tech Corp',
                        'experience': 'Advanced',
                        'dietary_requirements': 'Vegetarian'
                    }
                },
                {
                    'participant_name': 'Jane Smith',
                    'participant_email': 'jane.smith@example.com',
                    'participant_phone': '+1-555-0124',
                    'status': 'pending',
                    'field_data': {
                        'company': 'StartupXYZ',
                        'experience': 'Intermediate',
                        'dietary_requirements': ''
                    }
                },
                {
                    'participant_name': 'Bob Johnson',
                    'participant_email': 'bob.johnson@example.com',
                    'participant_phone': '+1-555-0125',
                    'status': 'pending',
                    'field_data': {
                        'company': 'Freelancer',
                        'experience': 'Beginner',
                        'dietary_requirements': 'No allergies'
                    }
                }
            ]

            for reg_data in registrations_data:
                field_data = reg_data.pop('field_data')
                registration = Registration.objects.create(event=event, **reg_data)
                
                # Create field data entries
                for field_name, value in field_data.items():
                    event_field = EventField.objects.filter(event=event, field_name=field_name).first()
                    if event_field:
                        RegistrationFormFieldData.objects.create(
                            registration=registration,
                            event_field=event_field,
                            field_value=value
                        )
            
            self.stdout.write(self.style.SUCCESS('Created test registrations'))

        self.stdout.write(self.style.SUCCESS('Test data creation completed!'))
        self.stdout.write(f'Event ID: {event.id}')
        self.stdout.write('Admin login: admin / admin123')
