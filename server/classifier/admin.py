from django.contrib import admin
from .models import Email

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ['subject', 'sender', 'category', 'created_at', 'confidence_score', 'user_ip']
    list_filter = ['category', 'created_at', 'user_ip']
    search_fields = ['subject', 'content', 'sender', 'user_ip']
    readonly_fields = ['category', 'suggested_response', 'created_at', 'confidence_score', 'user_ip']
    fieldsets = (
        ('Informações do Email', {
            'fields': ('sender', 'subject', 'content')
        }),
        ('Classificação', {
            'fields': ('category', 'suggested_response', 'confidence_score')
        }),
        ('Metadata', {
            'fields': ('created_at', 'user_ip')
        }),
    )
