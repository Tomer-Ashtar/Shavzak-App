from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Worker
from .forms import WorkerForm


class WorkerListView(ListView):
    """View to display all workers."""
    model = Worker
    template_name = 'workers/list.html'
    context_object_name = 'workers'
    
    def get_queryset(self):
        return Worker.objects.all()


class WorkerCreateView(CreateView):
    """View to create a new worker."""
    model = Worker
    form_class = WorkerForm
    template_name = 'workers/worker_form.html'
    success_url = reverse_lazy('workers:list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Worker "{form.instance.name}" created successfully!')
        return super().form_valid(form)


class WorkerUpdateView(UpdateView):
    """View to update an existing worker."""
    model = Worker
    form_class = WorkerForm
    template_name = 'workers/worker_form.html'
    success_url = reverse_lazy('workers:list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Worker "{form.instance.name}" updated successfully!')
        return super().form_valid(form)


class WorkerDeleteView(DeleteView):
    """View to delete a worker."""
    model = Worker
    success_url = reverse_lazy('workers:list')
    
    def delete(self, request, *args, **kwargs):
        worker = self.get_object()
        messages.success(request, f'Worker "{worker.name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)
