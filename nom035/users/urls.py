from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('employees/', views.employees_view, name='employees_view'),
    path('employees/<int:employee_id>/', views.employee_details_view, 
        name='employee_details_view'),
]
