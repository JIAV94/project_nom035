from django.urls import path
from . import views

app_name = 'surveys'

urlpatterns = [
    path('', views.surveys_view, name='surveys_view'),
    path('<int:survey_id>', views.survey_details_view, name='survey_details_view'),
    path('create_survey', views.create_survey, name='create_survey'),
    path('respond_survey/<int:survey_id>', views.respond_survey, name='respond_survey'),
]
