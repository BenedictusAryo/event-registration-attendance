from django.contrib import admin
from .models import Event, EventField, Registration, RegistrationFormFieldData

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'organizer', 'start_date', 'location', 'is_published', 'total_registrations']
    list_filter = ['is_published', 'start_date', 'created_at']
    search_fields = ['name', 'location', 'organizer__username']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    
    def total_registrations(self, obj):
        return obj.total_registrations
    total_registrations.short_description = 'Registrations'

@admin.register(EventField)
class EventFieldAdmin(admin.ModelAdmin):
    list_display = ['field_name', 'event', 'field_type', 'is_required', 'order']
    list_filter = ['field_type', 'is_required', 'event']
    search_fields = ['field_name', 'event__name']
    ordering = ['event', 'order', 'id']

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ['participant_name', 'event', 'participant_email', 'status', 'registered_at']
    list_filter = ['status', 'event', 'registered_at']
    search_fields = ['participant_name', 'participant_email', 'participant_phone']
    readonly_fields = ['unique_id', 'qr_code_image', 'registered_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('event')

@admin.register(RegistrationFormFieldData)
class RegistrationFormFieldDataAdmin(admin.ModelAdmin):
    list_display = ['registration', 'event_field', 'field_value_short']
    list_filter = ['event_field__field_type', 'registration__event']
    search_fields = ['registration__participant_name', 'event_field__field_name', 'field_value']
    
    def field_value_short(self, obj):
        return obj.field_value[:50] + "..." if len(obj.field_value) > 50 else obj.field_value
    field_value_short.short_description = 'Field Value'
