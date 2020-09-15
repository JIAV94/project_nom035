from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
    path('employees/retrieve/<int:employee_id>', load_employee_data, name='load_employee_data'),
    path('employees/register/', register_employee, name='register_employee'),
    path('employees/update/<int:employee_id>', update_employee, name='update_employee'),
    path('employees/delete/<int:employee_id>', delete_employee, name='delete_employee'),
    path('employees/', employees_view, name='employees_view'),
    path('employees/<int:employee_id>/<int:survey_id>', employee_answers_view, 
        name='employee_answers_view'),
    path('employees/<int:employee_id>', employee_details_view, 
        name='employee_details_view'),
    path('policy/', policy_view, name='policy_view'),
]
