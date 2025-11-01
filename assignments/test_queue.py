from django.test import TestCase
from datetime import date
from workers.models import Worker
from assignments.models import Assignment
from assignments.queue_manager import QueueManager


class QueueManagerTest(TestCase):
    """Test cases for QueueManager."""
    
    def setUp(self):
        """Set up test data."""
        # Create workers with different counters
        self.worker1 = Worker.objects.create(
            name="Worker One",
            title="soldier",
            hard_chores_counter=0,
            outer_partner_counter=0
        )
        self.worker2 = Worker.objects.create(
            name="Worker Two",
            title="soldier",
            hard_chores_counter=5,
            outer_partner_counter=3
        )
        self.worker3 = Worker.objects.create(
            name="Worker Three",
            title="soldier",
            hard_chores_counter=2,
            outer_partner_counter=1
        )
        self.commander = Worker.objects.create(
            name="Commander One",
            title="commander",
            hard_chores_counter=1,
            outer_partner_counter=2
        )
        
        self.today = date.today()
    
    def test_get_next_suggestion_kitchen(self):
        """Test getting suggestion for kitchen task."""
        qm = QueueManager(task_type='kitchen', assignment_date=self.today)
        suggested = qm.get_next_suggestion()
        
        # Should suggest worker with lowest hard_chores_counter
        self.assertEqual(suggested, self.worker1)
    
    def test_get_next_suggestion_patrol(self):
        """Test getting suggestion for patrol task."""
        qm = QueueManager(task_type='patrol_a', assignment_date=self.today)
        suggested = qm.get_next_suggestion()
        
        # Should suggest worker with lowest outer_partner_counter
        self.assertEqual(suggested, self.worker1)
    
    def test_get_next_suggestion_commander_only(self):
        """Test getting commander suggestion."""
        qm = QueueManager(task_type='patrol_a', assignment_date=self.today)
        suggested = qm.get_next_suggestion(commanders_only=True)
        
        # Should suggest the commander
        self.assertEqual(suggested, self.commander)
    
    def test_accept_suggestion_creates_assignment(self):
        """Test accepting a suggestion creates an assignment."""
        qm = QueueManager(task_type='kitchen', assignment_date=self.today)
        worker = qm.get_next_suggestion()
        
        initial_counter = worker.hard_chores_counter
        assignment = qm.accept_suggestion(worker)
        
        # Assignment should be created
        self.assertIsNotNone(assignment)
        self.assertEqual(assignment.worker, worker)
        self.assertEqual(assignment.task_type, 'kitchen')
        
        # Counter should be incremented
        worker.refresh_from_db()
        self.assertEqual(worker.hard_chores_counter, initial_counter + 1)
    
    def test_accept_suggestion_increments_correct_counter(self):
        """Test that correct counter is incremented based on task type."""
        # Kitchen task
        qm_kitchen = QueueManager(task_type='kitchen', assignment_date=self.today)
        initial_hc = self.worker1.hard_chores_counter
        qm_kitchen.accept_suggestion(self.worker1)
        self.worker1.refresh_from_db()
        self.assertEqual(self.worker1.hard_chores_counter, initial_hc + 1)
        
        # Patrol task
        qm_patrol = QueueManager(task_type='patrol_a', assignment_date=self.today)
        initial_op = self.worker2.outer_partner_counter
        qm_patrol.accept_suggestion(self.worker2)
        self.worker2.refresh_from_db()
        self.assertEqual(self.worker2.outer_partner_counter, initial_op + 1)
    
    def test_already_assigned_workers_excluded(self):
        """Test that already assigned workers are excluded from suggestions."""
        # Assign worker1 to kitchen
        Assignment.objects.create(
            date=self.today,
            task_type='kitchen',
            worker=self.worker1
        )
        
        qm = QueueManager(task_type='kitchen', assignment_date=self.today)
        suggested = qm.get_next_suggestion()
        
        # Should not suggest worker1 (already assigned)
        self.assertNotEqual(suggested, self.worker1)
        # Should suggest commander (lowest counter=1 among available)
        self.assertEqual(suggested, self.commander)
    
    def test_guard_duty_excludes_workers_from_all_slots(self):
        """Test that guard duty excludes workers assigned to ANY time slot."""
        # Assign worker1 to a guard duty slot
        Assignment.objects.create(
            date=self.today,
            time_slot='07:00-09:00',
            task_type='guard_duty',
            worker=self.worker1
        )
        
        # Try to get suggestion for a different time slot
        qm = QueueManager(
            task_type='guard_duty',
            assignment_date=self.today,
            time_slot='09:00-11:00'
        )
        suggested = qm.get_next_suggestion()
        
        # Should not suggest worker1 (assigned to another guard slot)
        self.assertNotEqual(suggested, self.worker1)
    
    def test_manual_assign(self):
        """Test manual assignment of a specific worker."""
        qm = QueueManager(task_type='kitchen', assignment_date=self.today)
        assignment = qm.manual_assign(worker_id=self.worker2.id)
        
        self.assertIsNotNone(assignment)
        self.assertEqual(assignment.worker, self.worker2)
    
    def test_no_available_workers(self):
        """Test when no workers are available."""
        # Assign all workers
        for worker in [self.worker1, self.worker2, self.worker3, self.commander]:
            Assignment.objects.create(
                date=self.today,
                task_type='kitchen',
                worker=worker
            )
        
        qm = QueueManager(task_type='kitchen', assignment_date=self.today)
        suggested = qm.get_next_suggestion()
        
        self.assertIsNone(suggested)

