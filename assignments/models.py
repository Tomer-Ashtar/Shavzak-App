from django.db import models
from workers.models import Worker


class Assignment(models.Model):
    """Model representing a worker assignment to a task."""
    
    TASK_TYPE_CHOICES = [
        ('guard_duty', 'Guard Duty'),
        ('patrol_a', 'Patrol A'),
        ('patrol_b', 'Patrol B'),
        ('kitchen', 'Kitchen'),
    ]
    
    TIME_SLOT_CHOICES = [
        ('07:00-09:00', '07:00-09:00'),
        ('09:00-11:00', '09:00-11:00'),
        ('11:00-13:00', '11:00-13:00'),
        ('13:00-15:00', '13:00-15:00'),
        ('15:00-17:00', '15:00-17:00'),
        ('17:00-19:00', '17:00-19:00'),
        ('19:00-21:00', '19:00-21:00'),
        ('21:00-23:00', '21:00-23:00'),
        ('23:00-01:00', '23:00-01:00'),
        ('01:00-03:00', '01:00-03:00'),
        ('03:00-05:00', '03:00-05:00'),
        ('05:00-07:00', '05:00-07:00'),
    ]
    
    date = models.DateField()
    time_slot = models.CharField(
        max_length=20, 
        choices=TIME_SLOT_CHOICES, 
        blank=True, 
        null=True,
        help_text="Time slot for guarding tasks. Leave empty for full-day tasks."
    )
    task_type = models.CharField(max_length=50, choices=TASK_TYPE_CHOICES)
    worker = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=True)
    is_commander = models.BooleanField(
        default=False,
        help_text="Indicates if this worker is the commander for this patrol assignment"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date', 'time_slot', 'task_type']
        unique_together = [['date', 'time_slot', 'task_type', 'worker']]
    
    def __str__(self):
        worker_name = self.worker.name if self.worker else "Unassigned"
        if self.time_slot:
            return f"{self.get_task_type_display()} - {self.time_slot} - {worker_name} ({self.date})"
        else:
            return f"{self.get_task_type_display()} - {worker_name} ({self.date})"
    
    def is_time_slotted_task(self):
        """Check if this is a time-slotted task."""
        return self.task_type == 'guard_duty'
    
    def is_full_day_task(self):
        """Check if this is a full-day task."""
        return self.task_type in ['kitchen', 'patrol_a', 'patrol_b']
    
    @staticmethod
    def get_required_workers_for_slot(time_slot):
        """Get the number of required workers for a given time slot."""
        daytime_slots = ['07:00-09:00', '09:00-11:00', '11:00-13:00', '13:00-15:00', '15:00-17:00']
        return 1 if time_slot in daytime_slots else 2
