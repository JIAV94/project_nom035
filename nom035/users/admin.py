from django.contrib import admin
from .models import Employee, Company, InformationLog


admin.site.register(Company)
admin.site.register(Employee)
admin.site.register(InformationLog)