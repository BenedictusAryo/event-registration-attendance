from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
import json

class Event(models.Model):
    id = models.AutoField(primary_key=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='event_images/', blank=True, null=True, help_text='Optional event image')
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=300)
    is_published = models.BooleanField(default=False)
    registration_open_date = models.DateTimeField(null=True, blank=True)
    registration_close_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure unique slug
            counter = 1
            original_slug = self.slug
            while Event.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('events:event_detail', kwargs={'pk': self.pk})

    def get_registration_url(self):
        return reverse('events:event_register', kwargs={'slug': self.slug})

    @property
    def total_registrations(self):
        return self.registrations.count()

    @property
    def total_attended(self):
        return self.registrations.filter(status='attended').count()
    
    @property
    def registration_qr_code(self):
        """Generate base64 encoded QR code for registration URL"""
        from django.conf import settings
        import base64
        
        # Build full registration URL
        registration_url = f"{settings.SITE_URL}{self.get_registration_url()}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(registration_url)
        qr.make(fit=True)

        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to RGB if necessary
        if qr_img.mode != 'RGB':
            qr_img = qr_img.convert('RGB')

        # Convert to base64
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

class EventField(models.Model):
    FIELD_TYPE_CHOICES = [
        ('text', 'Text'),
        ('email', 'Email'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('textarea', 'Textarea'),
        ('radio', 'Radio Button'),
        ('checkbox', 'Checkbox'),
        ('select', 'Select Dropdown'),
        ('file', 'File Upload'),
        ('phone', 'Phone Number'),
    ]

    id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='fields')
    field_name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES)
    is_required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    choices = models.TextField(blank=True, help_text="For radio, checkbox, select fields. Enter choices separated by newlines.")
    placeholder = models.CharField(max_length=100, blank=True)
    help_text = models.CharField(max_length=200, blank=True)
    
    # Participant identifier fields
    is_participant_name = models.BooleanField(default=False, help_text="Use this field as participant name")
    is_participant_email = models.BooleanField(default=False, help_text="Use this field as participant email")
    is_participant_phone = models.BooleanField(default=False, help_text="Use this field as participant phone")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']
        unique_together = ['event', 'field_name']

    def __str__(self):
        return f"{self.event.name} - {self.field_name}"

    def get_choices_list(self):
        """Convert choices text to list"""
        if self.choices:
            return [choice.strip() for choice in self.choices.split('\n') if choice.strip()]
        return []

    def set_choices_list(self, choices_list):
        """Convert list to choices text"""
        self.choices = '\n'.join(choices_list)

class Registration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('attended', 'Attended'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    unique_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    registered_at = models.DateTimeField(auto_now_add=True)
    qr_code_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    attended_at = models.DateTimeField(null=True, blank=True)
    
    # Cache commonly accessed fields for performance
    participant_name = models.CharField(max_length=200, blank=True)
    participant_email = models.EmailField(blank=True)
    participant_phone = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['-registered_at']

    def __str__(self):
        return f"{self.event.name} - {self.participant_name or 'Registration'} ({self.unique_id})"

    def save(self, *args, **kwargs):
        # Generate QR code if not exists
        if not self.qr_code_image:
            self.generate_qr_code()
        super().save(*args, **kwargs)

    @property
    def qr_code(self):
        """Generate base64 encoded QR code for this registration"""
        import base64
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(str(self.unique_id))
        qr.make(fit=True)

        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to RGB if necessary
        if qr_img.mode != 'RGB':
            qr_img = qr_img.convert('RGB')

        # Convert to base64
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def generate_qr_code(self):
        """Generate QR code for this registration"""
        qr_data = str(self.unique_id)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to RGB if necessary
        if qr_img.mode != 'RGB':
            qr_img = qr_img.convert('RGB')        # Save to BytesIO
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Save to model
        filename = f'qr_code_{self.unique_id}.png'
        self.qr_code_image.save(filename, File(buffer), save=False)

    def get_field_data(self):
        """Get all form field data as dictionary"""
        data = {}
        for field_data in self.field_data.all():
            data[field_data.event_field.field_name] = field_data.field_value
        return data

    def update_cached_fields(self):
        """Update cached participant info from form data based on field identifiers"""
        field_data = self.get_field_data()
        
        # Find fields marked as participant identifiers
        name_fields = self.event.fields.filter(is_participant_name=True)
        email_fields = self.event.fields.filter(is_participant_email=True)
        phone_fields = self.event.fields.filter(is_participant_phone=True)
        
        # Set participant name (use first marked field, or combine multiple)
        if name_fields.exists():
            name_values = []
            for field in name_fields:
                if field.field_name in field_data:
                    name_values.append(field_data[field.field_name])
            self.participant_name = ' '.join(name_values) if name_values else ''
        
        # Set participant email (use first marked field)
        if email_fields.exists():
            for field in email_fields:
                if field.field_name in field_data:
                    self.participant_email = field_data[field.field_name]
                    break
        
        # Set participant phone (use first marked field)
        if phone_fields.exists():
            for field in phone_fields:
                if field.field_name in field_data:
                    self.participant_phone = field_data[field.field_name]
                    break

class RegistrationFormFieldData(models.Model):
    id = models.AutoField(primary_key=True)
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name='field_data')
    event_field = models.ForeignKey(EventField, on_delete=models.CASCADE)
    field_value = models.TextField()

    class Meta:
        unique_together = ['registration', 'event_field']

    def __str__(self):
        return f"{self.registration} - {self.event_field.field_name}: {self.field_value[:50]}"

    def get_display_value(self):
        """Get formatted display value based on field type"""
        if self.event_field.field_type in ['checkbox'] and self.field_value:
            try:
                # Handle multiple checkbox values
                values = json.loads(self.field_value)
                return ', '.join(values) if isinstance(values, list) else self.field_value
            except (json.JSONDecodeError, TypeError):
                return self.field_value
        return self.field_value