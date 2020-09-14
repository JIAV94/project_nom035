from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from users.views import is_company
from .models import *

# Finished
def surveys_view(request):
    user = request.user
    if user.is_authenticated and is_company(user) is not None:
        surveys = user.company.surveys.order_by('-id')
        context = {
            'surveys': surveys,
        }
        return render(request, 'surveys/survey_list.html', context)
    else:
        return redirect(_404(request, 'Page not found', '404.html'))


def survey_details_view(request, survey_id):
    return render(request, 'surveys/survey_details.html')

# Finished
def create_survey(request):
    user = request.user
    company = is_company(user)
    if company is not None:
        if request.method == 'POST':
            responsible = request.POST["responsible"]
            main_activities = request.POST["main_activities"]
            responsible_id = request.POST["responsible_id"]
            if responsible_id == "":
                responsible_id = 0
            employees = company.employees.all()
            company_size = employees.count()
            filenames = ['./nom035/static/surveys/guide_I.txt']
            if company_size > 50:
                filenames.append('./nom035/static/surveys/guide_III.txt')
            elif company_size > 15:
                filenames.append('./nom035/static/surveys/guide_II.txt')
            for filename in filenames:
                survey = None
                section = None
                with open(filename, encoding='utf-8') as survey_guide:
                    for line in survey_guide.readlines()[1:]:
                        data = line.split('|')
                        if data[0].isdigit():
                            survey = Survey.objects.create(
                              company=company, main_activities=main_activities,
                              guide_number=data[0], responsible=responsible,
                              responsible_id=responsible_id, title=data[2] 
                            )
                        elif data[0] == "Section":
                            section = Section.objects.create(
                              survey=survey, content=data[2], section_type=data[1]
                            )
                        else:
                            Question.objects.create(
                              section=section, number=data[1], content=data[2],
                              inverted=data[3]
                            )
                    asign_survey(survey, employees)
            return redirect('survey:surveys_view')
        else:
            return redirect('survey:surveys_view')
    else:
        return redirect(_404(request, 'Page not found', '404.html'))

# Finished
def asign_survey(survey, employees):
    for employee in employees:
        info_log = employee.information_logs.last()
        AnswerSheet.objects.create(
          employee=employee, information_log=info_log, survey=survey
        )
    return 0

# Finished
def update_survey(request, survey_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            company = is_company(request.user)
            if company is not None:
                survey = get_object_or_404(Survey, id=survey_id)
                if survey.company == company:
                    responsible = request.POST["responsible"]
                    responsible_id = request.POST["responsible_id"]
                    main_activities = request.POST["main_activities"]
                    conclusions = ""
                    method = ""
                    objective = ""
                    recommendations = ""
                    if conclusions in request.POST:
                        conclusions = request.POST["conclusions"]
                    if method in request.POST:
                        method = request.POST["method"]
                    if objective in request.POST:
                        objective = request.POST["objective"]
                    if recommendations in request.POST:
                        recommendations = request.POST["recommendations"]
                    survey.responsible = responsible
                    survey.responsible_id = responsible_id
                    survey.main_activities = main_activities
                    survey.conclusions = conclusions
                    survey.method = method
                    survey.objective = objective
                    survey.recommendations = recommendations
                    survey.save()
                    return redirect('survey:surveys_view')
            return redirect(_404(request, 'Page not found', '404.html'))
        return redirect('survey:surveys_view')
    return redirect('login_view')

# Finished
def load_survey_data(request, survey_id):
    if request.user.is_authenticated:
        company = is_company(request.user)
        if company is not None:
            survey = get_object_or_404(Survey, id=survey_id)
            if survey.company == company:
                survey = [{
                  "responsible":survey.responsible, 
                  "responsible_id":survey.responsible_id,
                  "conclusions":survey.conclusions,
                  "method":survey.method,
                  "objective":survey.objective,
                  "recommendations":survey.recommendations,
                  "main_activities":survey.main_activities
                }]
                return JsonResponse(survey, content_type='application/json', safe=False)
        return redirect(_404(request, 'Page not found', '404.html'))
    return redirect('login_view')


def respond_survey(request, survey_id):
    survey = Survey.objects.get(id=survey_id)
    context = {
      'survey': survey
    }
    return render(request,'surveys/survey_form.html', context)