from django.shortcuts import render
from django.http import HttpResponse


def login_view(request):
    return render(request,'login.html')


def index_view(request):
    return render(request, 'users/index.html')
    

def employees_view(request):
    return render(request, 'users/employee_list.html')
    

def employee_details_view(request, employee_id):
    return render(request, 'users/employee_details.html')
