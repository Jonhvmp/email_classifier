from django.contrib import admin
from .models import Email

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ['subject', 'sender', 'category', 'created_at', 'confidence_score']
    list_filter = ['category', 'created_at']
    search_fields = ['subject', 'content', 'sender']
    readonly_fields = ['category', 'suggested_response', 'created_at', 'confidence_score']
    fieldsets = (
        ('Informações do Email', {
            'fields': ('sender', 'subject', 'content')
        }),
        ('Classificação', {
            'fields': ('category', 'suggested_response')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
