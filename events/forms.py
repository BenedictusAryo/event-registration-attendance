from django import forms
from .models import Event, EventField, Registration, RegistrationFormFieldData
import json

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'name', 'description', 'image', 'start_date', 'end_date', 
            'start_time', 'end_time', 'location', 'is_published',
            'registration_open_date', 'registration_close_date'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter event name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter event description'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter event location'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'registration_open_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'registration_close_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

class EventFieldForm(forms.ModelForm):
    class Meta:
        model = EventField
        fields = [
            'field_name', 'field_type', 'is_required', 'order',
            'choices', 'placeholder', 'help_text',
            'is_participant_name', 'is_participant_email', 'is_participant_phone'
        ]
        widgets = {
            'field_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Full Name'}),
            'field_type': forms.Select(attrs={'class': 'form-control'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'choices': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Enter choices (one per line)'
            }),
            'placeholder': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Placeholder text'}),
            'help_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Help text'}),
            'is_participant_name': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_participant_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_participant_phone': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class DynamicRegistrationForm(forms.Form):
    def __init__(self, event, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = event
        
        for field in event.fields.all().order_by('order', 'id'):
            field_kwargs = {
                'required': field.is_required,
                'label': field.field_name,
                'help_text': field.help_text,
            }
            
            # Handle widgets based on field type and placeholder
            if field.field_type == 'text':
                if field.placeholder:
                    field_kwargs['widget'] = forms.TextInput(attrs={'class': 'form-control', 'placeholder': field.placeholder})
                else:
                    field_kwargs['widget'] = forms.TextInput(attrs={'class': 'form-control'})
                self.fields[f'field_{field.id}'] = forms.CharField(**field_kwargs)
                
            elif field.field_type == 'email':
                if field.placeholder:
                    field_kwargs['widget'] = forms.EmailInput(attrs={'class': 'form-control', 'placeholder': field.placeholder})
                else:
                    field_kwargs['widget'] = forms.EmailInput(attrs={'class': 'form-control'})
                self.fields[f'field_{field.id}'] = forms.EmailField(**field_kwargs)
                
            elif field.field_type == 'number':
                if field.placeholder:
                    field_kwargs['widget'] = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': field.placeholder})
                else:
                    field_kwargs['widget'] = forms.NumberInput(attrs={'class': 'form-control'})
                self.fields[f'field_{field.id}'] = forms.IntegerField(**field_kwargs)
                
            elif field.field_type == 'date':
                field_kwargs['widget'] = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
                self.fields[f'field_{field.id}'] = forms.DateField(**field_kwargs)
                
            elif field.field_type == 'textarea':
                if field.placeholder:
                    field_kwargs['widget'] = forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': field.placeholder})
                else:
                    field_kwargs['widget'] = forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
                self.fields[f'field_{field.id}'] = forms.CharField(**field_kwargs)
                
            elif field.field_type == 'phone':
                if field.placeholder:
                    field_kwargs['widget'] = forms.TextInput(attrs={'class': 'form-control', 'type': 'tel', 'placeholder': field.placeholder})
                else:
                    field_kwargs['widget'] = forms.TextInput(attrs={'class': 'form-control', 'type': 'tel'})
                self.fields[f'field_{field.id}'] = forms.CharField(max_length=20, **field_kwargs)
                
            elif field.field_type == 'radio':
                choices = [(choice.strip(), choice.strip()) for choice in field.get_choices_list()]
                field_kwargs['widget'] = forms.RadioSelect(attrs={'class': 'form-check-input'})
                self.fields[f'field_{field.id}'] = forms.ChoiceField(choices=choices, **field_kwargs)
                
            elif field.field_type == 'select':
                choices = [('', '-- Select --')] + [(choice.strip(), choice.strip()) for choice in field.get_choices_list()]
                field_kwargs['widget'] = forms.Select(attrs={'class': 'form-control'})
                self.fields[f'field_{field.id}'] = forms.ChoiceField(choices=choices, **field_kwargs)
                
            elif field.field_type == 'checkbox':
                choices = [(choice.strip(), choice.strip()) for choice in field.get_choices_list()]
                field_kwargs['widget'] = forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
                self.fields[f'field_{field.id}'] = forms.MultipleChoiceField(choices=choices, **field_kwargs)
                
            elif field.field_type == 'file':
                field_kwargs['widget'] = forms.FileInput(attrs={'class': 'form-control'})
                self.fields[f'field_{field.id}'] = forms.FileField(**field_kwargs)

    def save(self, commit=True):
        if not commit:
            return None
            
        # Create registration
        registration = Registration.objects.create(event=self.event)
        
        # Save field data
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('field_'):
                field_id = int(field_name.split('_')[1])
                event_field = EventField.objects.get(id=field_id)
                
                # Handle multiple choice fields (checkboxes)
                if isinstance(value, list):
                    value = json.dumps(value)
                
                RegistrationFormFieldData.objects.create(
                    registration=registration,
                    event_field=event_field,
                    field_value=str(value)
                )
        
        # Update cached participant fields
        registration.update_cached_fields()
        registration.save()
        
        return registration
