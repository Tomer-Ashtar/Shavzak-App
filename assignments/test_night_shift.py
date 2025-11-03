from django.test import TestCase, Client
from django.urls import reverse
from datetime import date
from workers.models import Worker
from assignments.models import Assignment


class NightShiftCounterTest(TestCase):
    """Test cases for night shift hard chores counter."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.worker = Worker.objects.create(
            name="Test Worker",
            title="soldier",
            hard_chores_counter=5
        )
        self.today = date.today()
    
    def test_night_shift_increments_counter(self):
        """Test that assigning to night shift increments hard_chores_counter."""
        initial_counter = self.worker.hard_chores_counter
        
        # Assign to night shift slot
        response = self.client.post(reverse('assignments:assign_worker'), {
            'date': self.today.isoformat(),
            'task_type': 'guard_duty',
            'time_slot': '01:00-03:00',
            'worker_id': self.worker.id
        })
        
        # Check counter increased
        self.worker.refresh_from_db()
        self.assertEqual(self.worker.hard_chores_counter, initial_counter + 1)
    
    def test_night_shift_03_05_increments_counter(self):
        """Test that 03:00-05:00 slot also increments counter."""
        initial_counter = self.worker.hard_chores_counter
        
        # Assign to the other night shift slot
        response = self.client.post(reverse('assignments:assign_worker'), {
            'date': self.today.isoformat(),
            'task_type': 'guard_duty',
            'time_slot': '03:00-05:00',
            'worker_id': self.worker.id
        })
        
        # Check counter increased
        self.worker.refresh_from_db()
        self.assertEqual(self.worker.hard_chores_counter, initial_counter + 1)
    
    def test_non_night_shift_does_not_increment(self):
        """Test that regular guard duty doesn't increment counter."""
        initial_counter = self.worker.hard_chores_counter
        
        # Assign to regular daytime slot
        response = self.client.post(reverse('assignments:assign_worker'), {
            'date': self.today.isoformat(),
            'task_type': 'guard_duty',
            'time_slot': '07:00-09:00',
            'worker_id': self.worker.id
        })
        
        # Counter should NOT change
        self.worker.refresh_from_db()
        self.assertEqual(self.worker.hard_chores_counter, initial_counter)
    
    def test_remove_night_shift_decrements_counter(self):
        """Test that removing from night shift decrements counter."""
        # Create night shift assignment
        assignment = Assignment.objects.create(
            date=self.today,
            task_type='guard_duty',
            time_slot='01:00-03:00',
            worker=self.worker
        )
        
        # Manually increment (as the view does)
        self.worker.hard_chores_counter += 1
        self.worker.save()
        initial_counter = self.worker.hard_chores_counter
        
        # Remove assignment
        response = self.client.post(
            reverse('assignments:remove_assignment', args=[assignment.id])
        )
        
        # Counter should decrease
        self.worker.refresh_from_db()
        self.assertEqual(self.worker.hard_chores_counter, initial_counter - 1)
    
    def test_remove_regular_guard_does_not_decrement(self):
        """Test that removing regular guard duty doesn't decrement counter."""
        # Create regular guard assignment
        assignment = Assignment.objects.create(
            date=self.today,
            task_type='guard_duty',
            time_slot='09:00-11:00',
            worker=self.worker
        )
        
        initial_counter = self.worker.hard_chores_counter
        
        # Remove assignment
        response = self.client.post(
            reverse('assignments:remove_assignment', args=[assignment.id])
        )
        
        # Counter should NOT change
        self.worker.refresh_from_db()
        self.assertEqual(self.worker.hard_chores_counter, initial_counter)
    
    def test_counter_does_not_go_below_zero(self):
        """Test that counter doesn't go below zero on removal."""
        # Set counter to 0
        self.worker.hard_chores_counter = 0
        self.worker.save()
        
        # Create and remove night shift assignment
        assignment = Assignment.objects.create(
            date=self.today,
            task_type='guard_duty',
            time_slot='03:00-05:00',
            worker=self.worker
        )
        
        response = self.client.post(
            reverse('assignments:remove_assignment', args=[assignment.id])
        )
        
        # Counter should stay at 0, not go negative
        self.worker.refresh_from_db()
        self.assertEqual(self.worker.hard_chores_counter, 0)

