from django.contrib import admin
from .models import Worker


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    """Admin interface for Worker model."""
    
    list_display = ['name', 'title', 'hard_chores_counter', 'outer_partner_counter', 'created_at']
    list_filter = ['title', 'created_at']
    search_fields = ['name', 'title']
    readonly_fields = ['created_at', 'updated_at']
