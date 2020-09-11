from django.db import models
from users.models import Employee, Company, InformationLog


class Survey(models.Model):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="surveys", default=1)
    title = models.CharField(max_length=150)
    responsible = models.CharField(max_length=70)
    responsible_id = models.IntegerField(blank=True)
    conclusions = models.TextField(default='')
    method = models.CharField(max_length=30, default='')
    objective = models.TextField(default='')
    recommendations = models.TextField(default='')
    main_activities = models.CharField(max_length=200)
    guide_number = models.IntegerField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.date}"


class Section(models.Model):
    survey = models.ForeignKey(
        'Survey', on_delete=models.CASCADE, related_name='sections')
    content = models.CharField(max_length=200, default='')

    def __str__(self):
        return f"{self.survey.guide_number} - {self.content}"


class Question(models.Model):
    section = models.ForeignKey(
        'Section', on_delete=models.CASCADE, related_name='questions')
    number = models.IntegerField()
    content = models.CharField(max_length=200, default='')
    inverted = models.BooleanField()

    def __str__(self):
        return f"{self.section.survey.guide_number} - {self.number} - {self.content}"


class AnswerSheet(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='answer_sheets', default=1)
    survey = models.ForeignKey(
        'Survey', on_delete=models.CASCADE, related_name='answer_sheets')
    information_log = models.ForeignKey(
        InformationLog, on_delete=models.CASCADE, related_name='answer_sheets')
    date = models.DateField(auto_now_add=True)
    final_answer = models.CharField(max_length=15, default='unanswered')

    def __str__(self):
        return f"{self.employee} - {self.survey}"


class Answer(models.Model):
    question = models.ForeignKey(
        'Question', on_delete=models.CASCADE, related_name='answers')
    answer_sheet = models.ForeignKey(
        'AnswerSheet', on_delete=models.CASCADE, related_name='answers')
    value = models.IntegerField()

    def __str__(self):
        return f"{self.question} - {self.value}"


class Grade(models.Model):
    answer_sheet = models.OneToOneField(
        'AnswerSheet', on_delete=models.CASCADE, related_name='grade')
    work_environment = models.CharField(max_length=10)
    activity_factor = models.CharField(max_length=10)
    time_organization = models.CharField(max_length=10)
    leadership_relationship = models.CharField(max_length=10)
    organizational_environment = models.CharField(max_length=10, blank=True)
    work_environment_conditions = models.CharField(max_length=10)
    working_load = models.CharField(max_length=10)
    work_lack_control = models.CharField(max_length=10)
    working_day = models.CharField(max_length=10)
    family_work_relationship = models.CharField(max_length=10)
    leadership = models.CharField(max_length=10)
    work_relationship = models.CharField(max_length=10)
    violence = models.CharField(max_length=10)
    performance_recognition = models.CharField(max_length=10, blank=True)
    sense_belonging_instability = models.CharField(max_length=10, blank=True)
