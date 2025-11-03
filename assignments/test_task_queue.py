from django.test import TestCase
from workers.models import Worker
from assignments.models import TaskQueue


class TaskQueueTest(TestCase):
    """Test cases for TaskQueue model and queue rotation."""
    
    def setUp(self):
        """Set up test data."""
        # Create workers
        self.worker1 = Worker.objects.create(name="Worker One", title="soldier")
        self.worker2 = Worker.objects.create(name="Worker Two", title="soldier")
        self.worker3 = Worker.objects.create(name="Worker Three", title="commander")
        
        # Initialize queues manually for kitchen
        TaskQueue.objects.create(worker=self.worker1, task_type='kitchen', position=0)
        TaskQueue.objects.create(worker=self.worker2, task_type='kitchen', position=1)
        TaskQueue.objects.create(worker=self.worker3, task_type='kitchen', position=2)
    
    def test_get_next_worker(self):
        """Test getting the next worker in queue."""
        next_worker = TaskQueue.get_next_worker('kitchen')
        self.assertEqual(next_worker, self.worker1)
    
    def test_move_to_end(self):
        """Test moving a worker to the end of the queue."""
        # Worker1 is at position 0
        TaskQueue.move_to_end(self.worker1, 'kitchen')
        
        # Check positions
        queue = TaskQueue.get_queue_for_task('kitchen')
        positions = [(q.worker.name, q.position) for q in queue]
        
        # Worker1 should be at position 2 (end)
        self.assertEqual(positions[0], ('Worker Two', 0))
        self.assertEqual(positions[1], ('Worker Three', 1))
        self.assertEqual(positions[2], ('Worker One', 2))
    
    def test_move_to_end_from_middle(self):
        """Test moving a worker from middle position to end."""
        # Move worker2 (position 1) to end
        TaskQueue.move_to_end(self.worker2, 'kitchen')
        
        queue = TaskQueue.get_queue_for_task('kitchen')
        positions = [(q.worker.name, q.position) for q in queue]
        
        # Order should be: worker1(0), worker3(1), worker2(2)
        self.assertEqual(positions[0], ('Worker One', 0))
        self.assertEqual(positions[1], ('Worker Three', 1))
        self.assertEqual(positions[2], ('Worker Two', 2))
    
    def test_queue_rotation_sequence(self):
        """Test full queue rotation sequence."""
        # Initial order: worker1, worker2, worker3
        
        # Assign worker1
        next1 = TaskQueue.get_next_worker('kitchen')
        self.assertEqual(next1, self.worker1)
        TaskQueue.move_to_end(self.worker1, 'kitchen')
        
        # Next should be worker2
        next2 = TaskQueue.get_next_worker('kitchen')
        self.assertEqual(next2, self.worker2)
        TaskQueue.move_to_end(self.worker2, 'kitchen')
        
        # Next should be worker3
        next3 = TaskQueue.get_next_worker('kitchen')
        self.assertEqual(next3, self.worker3)
        TaskQueue.move_to_end(self.worker3, 'kitchen')
        
        # Should cycle back to worker1
        next4 = TaskQueue.get_next_worker('kitchen')
        self.assertEqual(next4, self.worker1)
    
    def test_initialize_for_worker(self):
        """Test initializing queues for a new worker."""
        new_worker = Worker.objects.create(name="New Worker", title="soldier")
        TaskQueue.initialize_for_worker(new_worker)
        
        # Check that queue entries were created for all task types
        task_types = [choice[0] for choice in TaskQueue.TASK_TYPE_CHOICES]
        for task_type in task_types:
            self.assertTrue(
                TaskQueue.objects.filter(worker=new_worker, task_type=task_type).exists()
            )
    
    def test_get_queue_for_task(self):
        """Test retrieving full queue for a task."""
        queue = TaskQueue.get_queue_for_task('kitchen')
        
        # Should return 3 entries in order
        self.assertEqual(queue.count(), 3)
        self.assertEqual(queue[0].worker, self.worker1)
        self.assertEqual(queue[1].worker, self.worker2)
        self.assertEqual(queue[2].worker, self.worker3)
    
    def test_queue_positions_are_sequential(self):
        """Test that positions remain sequential after operations."""
        # Move first worker to end
        TaskQueue.move_to_end(self.worker1, 'kitchen')
        
        # Get all positions
        queue = TaskQueue.get_queue_for_task('kitchen')
        positions = [q.position for q in queue]
        
        # Should be [0, 1, 2]
        self.assertEqual(positions, [0, 1, 2])
    
    def test_move_to_front(self):
        """Test moving a worker to the front of the queue."""
        # Worker3 is at position 2
        TaskQueue.move_to_front(self.worker3, 'kitchen')
        
        queue = TaskQueue.get_queue_for_task('kitchen')
        positions = [(q.worker.name, q.position) for q in queue]
        
        # Worker3 should be at position 0
        self.assertEqual(positions[0], ('Worker Three', 0))
        self.assertEqual(positions[1], ('Worker One', 1))
        self.assertEqual(positions[2], ('Worker Two', 2))
    
    def test_assign_then_remove_cycle(self):
        """Test assign/remove cycle returns worker to front."""
        # Initial: worker1 at position 0
        initial_next = TaskQueue.get_next_worker('kitchen')
        self.assertEqual(initial_next, self.worker1)
        
        # Assign worker1
        TaskQueue.move_to_end(self.worker1, 'kitchen')
        
        # Worker1 should be at end now
        after_assign = TaskQueue.get_next_worker('kitchen')
        self.assertEqual(after_assign, self.worker2)
        
        # Remove assignment - move worker1 back to front
        TaskQueue.move_to_front(self.worker1, 'kitchen')
        
        # Worker1 should be back at position 0
        after_remove = TaskQueue.get_next_worker('kitchen')
        self.assertEqual(after_remove, self.worker1)

