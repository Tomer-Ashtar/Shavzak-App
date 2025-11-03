from django.db import models
from workers.models import Worker


class Assignment(models.Model):
    """Model representing a worker assignment to a task."""
    
    TASK_TYPE_CHOICES = [
        ('guard_duty', 'שמירה'),
        ('patrol_a', 'סיור א\''),
        ('patrol_b', 'סיור ב\''),
        ('kitchen', 'מטבח'),
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


class TaskQueue(models.Model):
    """Model representing a worker's position in the queue for a specific task type."""
    
    TASK_TYPE_CHOICES = Assignment.TASK_TYPE_CHOICES
    
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='task_queues')
    task_type = models.CharField(max_length=50, choices=TASK_TYPE_CHOICES)
    position = models.IntegerField(default=0, help_text="Queue position (0 = first in line)")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['worker', 'task_type']
        ordering = ['task_type', 'position']
        indexes = [
            models.Index(fields=['task_type', 'position']),
        ]
    
    def __str__(self):
        return f"{self.worker.name} - {self.get_task_type_display()} - Position {self.position}"
    
    @classmethod
    def get_queue_for_task(cls, task_type):
        """Get all workers in queue order for a specific task."""
        return cls.objects.filter(task_type=task_type).select_related('worker').order_by('position')
    
    @classmethod
    def get_next_worker(cls, task_type):
        """Get the worker at the head of the queue for a task."""
        queue_entry = cls.objects.filter(task_type=task_type).order_by('position').first()
        return queue_entry.worker if queue_entry else None
    
    @classmethod
    def move_to_end(cls, worker, task_type):
        """Move a worker to the end of the queue for a specific task."""
        from django.db import transaction
        
        with transaction.atomic():
            # Get all queue entries for this task, lock them
            all_entries = list(cls.objects.filter(task_type=task_type).select_for_update().order_by('position'))
            
            # Find the worker's current entry
            worker_queue = None
            for entry in all_entries:
                if entry.worker_id == worker.id:
                    worker_queue = entry
                    break
            
            # If worker not in queue, create entry at end
            if not worker_queue:
                max_position = len(all_entries) - 1 if all_entries else -1
                cls.objects.create(worker=worker, task_type=task_type, position=max_position + 1)
                return
            
            # Remove worker from current position
            all_entries.remove(worker_queue)
            
            # Reorder: assign new sequential positions
            for idx, entry in enumerate(all_entries):
                entry.position = idx
                entry.save()
            
            # Put worker at the end
            worker_queue.position = len(all_entries)
            worker_queue.save()
    
    @classmethod
    def move_to_front(cls, worker, task_type):
        """Move a worker to the front (position 0) of the queue for a specific task."""
        from django.db import transaction
        
        with transaction.atomic():
            # Get all queue entries for this task, lock them
            all_entries = list(cls.objects.filter(task_type=task_type).select_for_update().order_by('position'))
            
            # Find the worker's current entry
            worker_queue = None
            for entry in all_entries:
                if entry.worker_id == worker.id:
                    worker_queue = entry
                    break
            
            # If worker not in queue, create entry at front
            if not worker_queue:
                # Shift everyone down
                for entry in all_entries:
                    entry.position += 1
                    entry.save()
                cls.objects.create(worker=worker, task_type=task_type, position=0)
                return
            
            # Remove worker from current position
            all_entries.remove(worker_queue)
            
            # Reorder: assign new sequential positions starting from 1
            for idx, entry in enumerate(all_entries):
                entry.position = idx + 1
                entry.save()
            
            # Put worker at the front (position 0)
            worker_queue.position = 0
            worker_queue.save()
    
    @classmethod
    def initialize_for_worker(cls, worker):
        """Initialize queue entries for a new worker across all task types."""
        task_types = [choice[0] for choice in cls.TASK_TYPE_CHOICES]
        
        for task_type in task_types:
            # Get max position for this task
            max_position = cls.objects.filter(task_type=task_type).aggregate(
                models.Max('position')
            )['position__max'] or -1
            
            # Create queue entry at end
            cls.objects.get_or_create(
                worker=worker,
                task_type=task_type,
                defaults={'position': max_position + 1}
            )
