from django.urls import path
from . import views

app_name = 'assignments'

urlpatterns = [
    path('calendar/', views.calendar_view, name='calendar'),
    path('assign-worker/', views.assign_worker, name='assign_worker'),
    path('remove-assignment/<int:assignment_id>/', views.remove_assignment, name='remove_assignment'),
]

