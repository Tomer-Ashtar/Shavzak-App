from django.contrib import admin
from .models import Worker


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    """Admin interface for Worker model."""
    
    list_display = ['name', 'title', 'department', 'hard_chores_counter', 'outer_partner_counter', 'created_at']
    list_filter = ['title', 'department', 'created_at']
    search_fields = ['name', 'title', 'department']
    readonly_fields = ['created_at', 'updated_at']
