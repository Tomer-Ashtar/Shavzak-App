from django.contrib import admin
from .models import Assignment, TaskQueue


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


@admin.register(TaskQueue)
class TaskQueueAdmin(admin.ModelAdmin):
    """Admin interface for TaskQueue model."""
    
    list_display = ['worker', 'task_type', 'position', 'updated_at']
    list_filter = ['task_type']
    search_fields = ['worker__name']
    readonly_fields = ['updated_at']
    ordering = ['task_type', 'position']
    list_per_page = 100
    
    fieldsets = (
        ('Queue Details', {
            'fields': ('worker', 'task_type', 'position')
        }),
        ('Timestamps', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
