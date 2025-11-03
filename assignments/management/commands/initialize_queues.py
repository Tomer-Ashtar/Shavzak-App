from django.core.management.base import BaseCommand
from django.db.models import Max
from workers.models import Worker
from assignments.models import TaskQueue


class Command(BaseCommand):
    help = 'Initialize task queues for all workers'

    def handle(self, *args, **options):
        workers = Worker.objects.all()
        
        if not workers.exists():
            self.stdout.write(self.style.WARNING('No workers found. Create workers first.'))
            return
        
        # Get all task types
        task_types = [choice[0] for choice in TaskQueue.TASK_TYPE_CHOICES]
        
        created_count = 0
        
        for worker in workers:
            for task_type in task_types:
                # Check if queue entry already exists
                if not TaskQueue.objects.filter(worker=worker, task_type=task_type).exists():
                    # Get max position for this task
                    max_position = TaskQueue.objects.filter(task_type=task_type).aggregate(
                        Max('position')
                    )['position__max'] or -1
                    
                    # Create queue entry at end
                    TaskQueue.objects.create(
                        worker=worker,
                        task_type=task_type,
                        position=max_position + 1
                    )
                    created_count += 1
        
        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(
                f'Successfully initialized {created_count} queue entries'
            ))
        else:
            self.stdout.write(self.style.SUCCESS('All queues already initialized'))
        
        # Display current queues
        self.stdout.write('\nCurrent Queue Status:')
        for task_type, task_name in TaskQueue.TASK_TYPE_CHOICES:
            self.stdout.write(f'\n{task_name}:')
            queue = TaskQueue.objects.filter(task_type=task_type).select_related('worker').order_by('position')
            for entry in queue:
                self.stdout.write(f'  {entry.position}. {entry.worker.name} ({entry.worker.get_title_display()})')

