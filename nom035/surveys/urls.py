from django.urls import path
from .views import *

app_name = 'surveys'

urlpatterns = [
    path('', surveys_view, name='surveys_view'),
    path('<int:survey_id>', survey_details_view, name='survey_details_view'),
    path('create_survey', create_survey, name='create_survey'),
    path('retrieve/<int:survey_id>', load_survey_data, name='load_survey_data'),
    path('update/<int:survey_id>', update_survey, name='update_survey'),
    path('respond_survey/<int:survey_id>', respond_survey, name='respond_survey'),
]
