from django.test import TestCase, Client
from django.urls import reverse
from datetime import date
from .models import Assignment
from workers.models import Worker


class AssignmentModelTest(TestCase):
    """Test cases for Assignment model."""
    
    def setUp(self):
        """Set up test data."""
        self.worker = Worker.objects.create(
            name="Test Worker",
            title="soldier"
        )
        self.commander = Worker.objects.create(
            name="Test Commander",
            title="commander"
        )
    
    def test_guard_duty_assignment_creation(self):
        """Test creating a guard duty assignment with time slot."""
        assignment = Assignment.objects.create(
            date=date.today(),
            time_slot='07:00-09:00',
            task_type='guard_duty',
            worker=self.worker
        )
        self.assertEqual(assignment.task_type, 'guard_duty')
        self.assertEqual(assignment.time_slot, '07:00-09:00')
        self.assertTrue(assignment.is_time_slotted_task())
        self.assertFalse(assignment.is_full_day_task())
    
    def test_full_day_assignment_creation(self):
        """Test creating a full-day assignment without time slot."""
        assignment = Assignment.objects.create(
            date=date.today(),
            task_type='kitchen',
            worker=self.worker
        )
        self.assertEqual(assignment.task_type, 'kitchen')
        self.assertIsNone(assignment.time_slot)
        self.assertFalse(assignment.is_time_slotted_task())
        self.assertTrue(assignment.is_full_day_task())
    
    def test_patrol_full_day_assignment(self):
        """Test patrol assignment as full-day task."""
        assignment = Assignment.objects.create(
            date=date.today(),
            task_type='patrol_a',
            worker=self.commander,
            is_commander=True
        )
        self.assertEqual(assignment.task_type, 'patrol_a')
        self.assertIsNone(assignment.time_slot)
        self.assertTrue(assignment.is_full_day_task())
        self.assertTrue(assignment.is_commander)
    
    def test_required_workers_daytime(self):
        """Test required workers for daytime slot."""
        required = Assignment.get_required_workers_for_slot('07:00-09:00')
        self.assertEqual(required, 1)
    
    def test_required_workers_nighttime(self):
        """Test required workers for nighttime slot."""
        required = Assignment.get_required_workers_for_slot('19:00-21:00')
        self.assertEqual(required, 2)
    
    def test_assignment_str(self):
        """Test assignment string representation."""
        assignment = Assignment.objects.create(
            date=date.today(),
            time_slot='11:00-13:00',
            task_type='guard_duty',
            worker=self.worker
        )
        self.assertIn('Guard Duty', str(assignment))
        self.assertIn('11:00-13:00', str(assignment))
        self.assertIn(self.worker.name, str(assignment))


class CalendarViewTest(TestCase):
    """Test cases for Calendar view."""
    
    def setUp(self):
        """Set up test client and data."""
        self.client = Client()
        self.worker = Worker.objects.create(name="Test Worker", title="soldier")
        
        # Create some test assignments
        Assignment.objects.create(
            date=date.today(),
            time_slot='07:00-09:00',
            task_type='guard_duty',
            worker=self.worker
        )
        Assignment.objects.create(
            date=date.today(),
            task_type='kitchen',
            worker=self.worker
        )
    
    def test_calendar_view_loads(self):
        """Test calendar view loads correctly."""
        response = self.client.get(reverse('assignments:calendar'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Calendar (History)")
    
    def test_calendar_shows_assignments(self):
        """Test calendar displays assignments."""
        response = self.client.get(reverse('assignments:calendar'))
        self.assertContains(response, "Test Worker")
        self.assertContains(response, "07:00-09:00")
    
    def test_calendar_date_selection(self):
        """Test calendar with specific date."""
        test_date = date(2025, 1, 1)
        response = self.client.get(reverse('assignments:calendar'), {'date': test_date.isoformat()})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "January")
