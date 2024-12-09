from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    social_denomination = models.CharField(max_length=180)
    address = models.CharField(max_length=300)
    main_activity = models.CharField(max_length=200)
    employees_code = models.CharField(max_length=4)

    def __str__(self):
        return self.social_denomination


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(
        "Company", on_delete=models.CASCADE, related_name="employees"
    )
    sex = models.BooleanField(null=True)
    birthdate = models.DateField(default=timezone.now)
    policy = models.BooleanField(default=False)

    @property
    def age(self):
        import datetime

        return int((datetime.date.today() - self.birthdate).days / 365.25)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class InformationLog(models.Model):
    employee = models.ForeignKey(
        "Employee", on_delete=models.CASCADE, related_name="information_logs"
    )
    civil_status = models.IntegerField(null=True)
    educational_level = models.IntegerField(null=True)
    position = models.CharField(max_length=100, null=True)
    area = models.CharField(max_length=70, null=True)
    position_type = models.IntegerField(null=True)
    contract_type = models.IntegerField(null=True)
    personnel_type = models.IntegerField(null=True)
    working_day_type = models.IntegerField(null=True)
    shift_rotation = models.BooleanField(null=True)
    current_position_time = models.IntegerField(null=True)
    work_experience_time = models.IntegerField(null=True)
