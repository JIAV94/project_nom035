from django.contrib import admin
from django.contrib.auth.models import User
from .models import Employee, Company, InformationLog
from import_export import resources
from import_export.admin import ImportExportModelAdmin


class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = ('id', 'password', 'username', 'first_name', 
                  'last_name', 'email')


class UserAdmin(ImportExportModelAdmin):
    resource_class = UserResource


class EmployeeResource(resources.ModelResource):
    class Meta:
        model = Employee
        fields = ('id', 'user', 'company', 'sex', 'birthdate')


class EmployeeAdmin(ImportExportModelAdmin):
    resource_class = EmployeeResource


class InformationLogResource(resources.ModelResource):
    class Meta:
        model = InformationLog
        fields = ('id', 'employee', 'civil_status',
                  'educational_level', 'position', 'area',
                  'position_type', 'contract_type',
                  'personnel_type', 'working_day_type',
                  'shift_rotation', 'current_position_time',
                  'work_experience_time')

class InformationLogAdmin(ImportExportModelAdmin):
    resource_class = InformationLogResource


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Company)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(InformationLog, InformationLogAdmin)