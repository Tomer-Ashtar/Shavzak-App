from django.db import models


class Worker(models.Model):
    """Model representing a worker with their task counters."""
    
    TITLE_CHOICES = [
        ('commander', 'מפקד'),
        ('soldier', 'חייל'),
    ]
    
    DEPARTMENT_CHOICES = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('other', 'אחר'),
    ]
    
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=50, choices=TITLE_CHOICES)
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, blank=True, null=True, verbose_name='מחלקה')
    hard_chores_counter = models.IntegerField(default=0)
    outer_partner_counter = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.title})"
