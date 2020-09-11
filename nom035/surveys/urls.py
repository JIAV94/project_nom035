from django.urls import path
from . import views

app_name = 'surveys'

urlpatterns = [
    path('', views.surveys_view, name='surveys_view'),
    path('<int:survey_id>', views.survey_details_view, name='survey_details_view'),
    path('start_survey', views.start_survey, name='start_survey'),
]
