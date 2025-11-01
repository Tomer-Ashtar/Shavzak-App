from django.contrib import admin
from .models import Assignment


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    """Admin interface for Assignment model."""
    
    list_display = ['date', 'time_slot', 'task_type', 'worker', 'is_commander', 'created_at']
    list_filter = ['date', 'task_type', 'is_commander']
    search_fields = ['worker__name', 'task_type']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 50
    
    fieldsets = (
        ('Assignment Details', {
            'fields': ('date', 'task_type', 'time_slot', 'worker', 'is_commander')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
