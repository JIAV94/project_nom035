from django.shortcuts import render
from django.http import HttpResponse


def surveys_view(request):
    return render(request, 'surveys/survey_list.html')


def survey_details_view(request, survey_id):
    return render(request, 'surveys/survey_details.html')


def start_survey(request):
    return render(request, 'index_view')
