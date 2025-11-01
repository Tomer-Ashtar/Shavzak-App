from django.test import TestCase, Client
from django.urls import reverse
from .models import Worker


class WorkerModelTest(TestCase):
    """Test cases for Worker model."""
    
    def setUp(self):
        """Set up test data."""
        self.worker = Worker.objects.create(
            name="John Doe",
            title="commander",
            hard_chores_counter=5,
            outer_partner_counter=3
        )
    
    def test_worker_creation(self):
        """Test worker is created correctly."""
        self.assertEqual(self.worker.name, "John Doe")
        self.assertEqual(self.worker.title, "commander")
        self.assertEqual(self.worker.hard_chores_counter, 5)
        self.assertEqual(self.worker.outer_partner_counter, 3)
    
    def test_worker_str(self):
        """Test worker string representation."""
        self.assertEqual(str(self.worker), "John Doe (commander)")
    
    def test_default_counters(self):
        """Test default counter values."""
        worker = Worker.objects.create(name="Jane Smith", title="soldier")
        self.assertEqual(worker.hard_chores_counter, 0)
        self.assertEqual(worker.outer_partner_counter, 0)


class WorkerViewsTest(TestCase):
    """Test cases for Worker views."""
    
    def setUp(self):
        """Set up test client and data."""
        self.client = Client()
        self.worker = Worker.objects.create(
            name="Test Worker",
            title="soldier"
        )
    
    def test_worker_list_view(self):
        """Test workers list page loads correctly."""
        response = self.client.get(reverse('workers:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Worker")
        self.assertContains(response, "Soldier")
    
    def test_worker_create_view_get(self):
        """Test worker create form loads."""
        response = self.client.get(reverse('workers:add'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add New Worker")
    
    def test_worker_create_view_post(self):
        """Test worker creation via POST."""
        data = {
            'name': 'New Worker',
            'title': 'soldier',
            'hard_chores_counter': 0,
            'outer_partner_counter': 0
        }
        response = self.client.post(reverse('workers:add'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Worker.objects.filter(name='New Worker').exists())
    
    def test_worker_update_view(self):
        """Test worker update view."""
        response = self.client.get(reverse('workers:edit', args=[self.worker.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Worker")
        self.assertContains(response, "Test Worker")
    
    def test_worker_delete_view(self):
        """Test worker deletion."""
        response = self.client.post(reverse('workers:delete', args=[self.worker.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertFalse(Worker.objects.filter(pk=self.worker.pk).exists())
