from django.urls import path
from . import views

app_name = 'workers'

urlpatterns = [
    path('', views.WorkerListView.as_view(), name='list'),
    path('add/', views.WorkerCreateView.as_view(), name='add'),
    path('<int:pk>/edit/', views.WorkerUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.WorkerDeleteView.as_view(), name='delete'),
]
