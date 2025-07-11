from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'phone', 'created_at']
    search_fields = ['user__username', 'user__email', 'organization']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']
