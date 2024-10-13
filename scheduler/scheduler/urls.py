from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Add this line for the index page
    path('generate-employees/', views.generate_employee_data, name='generate_employees'),
    path('generate-tasks/', views.generate_task_data, name='generate_tasks'),
    path('assign-tasks/', views.assign_tasks, name='assign_tasks'),
]
