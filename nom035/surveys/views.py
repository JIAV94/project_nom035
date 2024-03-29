import json
import mimetypes
import os
from wsgiref.util import FileWrapper

import pandas as pd
from django.contrib import messages

# from django.core.files.temp import NamedTemporaryFile
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from users.views import _404, is_company, is_employee

from .models import Answer, AnswerSheet, Grade, Question, Section, Survey


def surveys_view(request):
    company = is_company(request.user)
    if request.user.is_authenticated and company is not None:
        surveys = company.surveys.order_by("-id")
        context = {
            "surveys": surveys,
        }
        return render(request, "surveys/survey_list.html", context)
    return redirect(_404(request, "Page not found", "404.html"))


def survey_report_view(request, survey_id):
    try:
        company = is_company(request.user)
        if request.user.is_authenticated and company is not None:
            survey = get_object_or_404(company.surveys, id=survey_id)
            sheets = AnswerSheet.objects.filter(survey=survey).exclude(
                final_answer="unanswered"
            )
            answered_count = sheets.count()
            value_map = {"Nulo": 0, "Bajo": 1, "Medio": 2, "Alto": 3, "Muy alto": 4}
            titles_mapping = {
                "work_environment": "Ambiente de trabajo",
                "activity_factor": "Factores propios de la actividad",
                "time_organization": "Organización del tiempo de trabajo",
                "leadership_relationship": "Liderazgo y relaciones en el trabajo",
                "organizational_environment": "Entorno organizacional",
                "work_environment_conditions": "Condiciones en el ambiente de trabajo",
                "working_load": "Carga de trabajo",
                "work_lack_control": "Falta de control sobre el trabajo",
                "working_day": "Jornada de trabajo",
                "family_work_relationship": "Interferencia en la relación trabajo y familia",
                "leadership": "Liderazgo",
                "work_relationship": "Relaciones en el trabajo",
                "violence": "Violencia",
                "performance_recognition": "Reconocimiento del desempeño",
                "sense_belonging_instability": "Insuficiente sentido de pertenencia e inestabilidad",
            }

            def init_report_structure(guide_number):
                report_structure = {
                    "category": {
                        "work_environment": [0] * 5,
                        "activity_factor": [0] * 5,
                        "time_organization": [0] * 5,
                        "leadership_relationship": [0] * 5,
                    },
                    "domain": {
                        "work_environment_conditions": [0] * 5,
                        "working_load": [0] * 5,
                        "work_lack_control": [0] * 5,
                        "working_day": [0] * 5,
                        "family_work_relationship": [0] * 5,
                        "leadership": [0] * 5,
                        "work_relationship": [0] * 5,
                        "violence": [0] * 5,
                    },
                }
                if guide_number == 3:
                    report_structure["category"]["organizational_environment"] = [0] * 5
                    report_structure["domain"].update(
                        {
                            "performance_recognition": [0] * 5,
                            "sense_belonging_instability": [0] * 5,
                        }
                    )
                return report_structure

            report = init_report_structure(survey.guide_number)
            for answer_sheet in sheets:
                grades = Grade.objects.filter(answer_sheet=answer_sheet.pk)
                for grade in grades:
                    for key in report:
                        for attribute in report[key]:
                            if hasattr(grade, attribute):
                                value = getattr(grade, attribute)
                                report[key][attribute][value_map[value]] += 1

            # Calculate percentages
            for category in report:
                for key, values in report[category].items():
                    report[category][key] = [
                        round((value / answered_count) * 100, 2) for value in values
                    ]

            report_for_template = []
            for category, values in report["category"].items():
                report_for_template.append(
                    {
                        "type": "category",
                        "name": titles_mapping[category],
                        "data": values,
                        "id": f"report_II_III_chart_{category}",
                    }
                )

            for domain, values in report["domain"].items():
                report_for_template.append(
                    {
                        "type": "domain",
                        "name": titles_mapping[domain],
                        "data": values,
                        "id": f"report_II_III_chart_{domain}",
                    }
                )

            context = {
                "survey": survey,
                "report": report_for_template,
            }
            return render(request, "surveys/survey_report.html", context)
    except Survey.DoesNotExist:
        return redirect(_404(request, "Page not found", "404.html"))


def survey_details_view(request, survey_id):
    company = is_company(request.user)
    try:
        if request.user.is_authenticated and company is not None:
            survey = company.surveys.get(id=survey_id)
            sheets = AnswerSheet.objects.filter(survey=survey)
            answered = sheets.exclude(final_answer="unanswered")
            unanswered = sheets.filter(final_answer="unanswered")
            context = {
                "survey": survey,
                "answered": answered,
                "unanswered": unanswered,
            }
            return render(request, "surveys/survey_details.html", context)
    except Survey.DoesNotExist:
        return redirect(_404(request, "Page not found", "404.html"))


def create_survey(request):
    user = request.user
    company = is_company(user)
    if request.user.is_authenticated and company is not None:
        if request.method == "POST":
            responsible = request.POST["responsible"]
            main_activities = request.POST["main_activities"]
            responsible_id = request.POST["responsible_id"]
            if responsible_id == "":
                responsible_id = 0
            employees = company.employees.all()
            company_size = employees.count()
            filenames = []
            if company_size > 50:
                filenames.append("./nom035/static/surveys/guide_III.txt")
            elif company_size > 15:
                filenames.append("./nom035/static/surveys/guide_II.txt")
            filenames.append("./nom035/static/surveys/guide_I.txt")
            for filename in filenames:
                survey = None
                section = None
                with open(filename, encoding="utf-8") as survey_guide:
                    for line in survey_guide.readlines()[1:]:
                        data = line.split("|")
                        if data[0].isdigit():
                            survey = Survey.objects.create(
                                company=company,
                                main_activities=main_activities,
                                guide_number=data[0],
                                responsible=responsible,
                                responsible_id=responsible_id,
                                title=data[2].strip(),
                            )
                        elif data[0] == "Section":
                            section = Section.objects.create(
                                survey=survey, content=data[2], section_type=data[1]
                            )
                        else:
                            Question.objects.create(
                                section=section,
                                number=data[1],
                                content=data[2],
                                inverted=data[3],
                            )
                    link_survey(survey, employees)
            return redirect("survey:surveys_view")
        else:
            return redirect("survey:surveys_view")
    else:
        return redirect(_404(request, "Page not found", "404.html"))


def link_survey(survey, employees):
    for employee in employees:
        info_log = employee.information_logs.last()
        AnswerSheet.objects.create(
            employee=employee, information_log=info_log, survey=survey
        )
    return 0


def assign_surveys(request):
    company = is_company(request.user)
    if request.user.is_authenticated and company is not None:
        if request.method == "POST":
            surveys = reversed(company.surveys.order_by("-id")[:2])
            for survey in surveys:
                employees = company.employees.all()
                for employee in employees:
                    if not employee.answer_sheets.filter(survey=survey).exists():
                        info_log = employee.information_logs.last()
                        AnswerSheet.objects.create(
                            survey=survey, employee=employee, information_log=info_log
                        )
            messages.success(
                request,
                "Los empleados faltantes se han asignado a las encuestas activas.",
            )
            return redirect("survey:surveys_view")
    return redirect(_404(request, "Page not found", "404.html"))


def update_survey(request, survey_id):
    company = is_company(request.user)
    if request.user.is_authenticated and company is not None:
        if request.method == "POST":
            survey = get_object_or_404(Survey, id=survey_id)
            if survey.company == company:
                responsible = request.POST["responsible"]
                responsible_id = request.POST["responsible_id"]
                main_activities = request.POST["main_activities"]
                conclusions = request.POST.get("conclusions", "")
                method = request.POST.get("method", "")
                objective = request.POST.get("objective", "")
                recommendations = request.POST.get("recommendations", "")
                survey.responsible = responsible
                survey.responsible_id = responsible_id
                survey.main_activities = main_activities
                survey.conclusions = conclusions
                survey.method = method
                survey.objective = objective
                survey.recommendations = recommendations
                survey.save()
                return redirect("survey:surveys_view")
            return redirect(_404(request, "Page not found", "404.html"))
    return redirect("index_view")


def load_survey_data(request, survey_id):
    company = is_company(request.user)
    if request.user.is_authenticated and company is not None:
        survey = get_object_or_404(Survey, id=survey_id)
        if survey.company == company:
            survey = [
                {
                    "responsible": survey.responsible,
                    "responsible_id": survey.responsible_id,
                    "conclusions": survey.conclusions,
                    "method": survey.method,
                    "objective": survey.objective,
                    "recommendations": survey.recommendations,
                    "main_activities": survey.main_activities,
                }
            ]
            return JsonResponse(survey, content_type="application/json", safe=False)
        return redirect(_404(request, "Page not found", "404.html"))
    return redirect("index_view")


def delete_survey(request, survey_id):
    try:
        company = is_company(request.user)
        if request.user.is_authenticated and company is not None:
            survey = company.surveys.get(id=survey_id)
            if survey.company == company:
                survey.delete()
                return redirect("survey:surveys_view")
    except Survey.DoesNotExist:
        return redirect(_404(request, "Page not found", "404.html"))


def respond_survey(request, survey_id):
    employee = is_employee(request.user)
    if request.user.is_authenticated and employee is not None:
        if request.method == "POST":
            info_log = employee.information_logs.last()
            survey = Survey.objects.get(id=survey_id)
            answer_sheet = employee.answer_sheets.get(survey=survey)
            if survey.guide_number == 1:
                grade_guide_I(request, survey, answer_sheet)
                return redirect("index_view")
            elif survey.guide_number == 2:
                dom, cat, final_ans = grade_guide_II(request, survey, answer_sheet)
                dom, cat, final_ans = value_to_text_II(dom, cat, final_ans)
            elif survey.guide_number == 3:
                dom, cat, final_ans = grade_guide_III(request, survey, answer_sheet)
                dom, cat, final_ans = value_to_text_III(dom, cat, final_ans)
            answer_sheet.information_log = info_log
            answer_sheet.final_answer = final_ans
            answer_sheet.save()
            Grade.objects.create(
                answer_sheet=answer_sheet,
                work_environment=cat[0],
                activity_factor=cat[1],
                time_organization=cat[2],
                leadership_relationship=cat[3],
                organizational_environment=cat[4],
                work_environment_conditions=dom[0],
                working_load=dom[1],
                work_lack_control=dom[2],
                working_day=dom[3],
                family_work_relationship=dom[4],
                leadership=dom[5],
                work_relationship=dom[6],
                violence=dom[7],
                performance_recognition=dom[8],
                sense_belonging_instability=dom[9],
            )
        else:
            survey = get_object_or_404(Survey, id=survey_id)
            context = {"survey": survey}
            return render(request, "surveys/survey_form.html", context)
    return redirect("index_view")


def grade_guide_I(request, survey, answer_sheet):
    sec_III = 0
    sec_IV = 0
    answer_sheet.final_answer = "No requiere atención clínica"
    for section in survey.sections.all():
        for question in section.questions.all():
            question_str = str(question.id)
            answer = request.POST[question_str]
            if answer == "0":
                if question.number == 1:
                    answer_sheet.save()
                    Answer.objects.create(
                        answer_sheet=answer_sheet,
                        question=question,
                        value=0,
                        content="No",
                    )
                    return
                content = "No"
                value = 0
            elif question.number > 1:
                if question.number < 4:
                    answer_sheet.final_answer = "Requiere atención clínica"
                elif question.number < 11:
                    sec_III += 1
                else:
                    sec_IV += 1
                content = "Si"
                value = 1
            else:
                content = "Si"
                value = 1
            Answer.objects.create(
                answer_sheet=answer_sheet,
                question=question,
                value=value,
                content=content,
            )
    if sec_III > 2 or sec_IV > 1:
        answer_sheet.final_answer = "Requiere atención clínica"
    answer_sheet.save()
    return


def grade_guide_II(request, survey, answer_sheet):
    wec = [1, 2, 3]  # Work environment conditions
    wl = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 41, 42, 43]  # Working load
    wlc = [18, 19, 20, 21, 22, 26, 27]  # Work lack control
    wd = [14, 15]  # Working day
    fwr = [16, 17]  # Family work relationship
    l = [23, 24, 25, 28, 29]  # Leadership
    wr = [30, 31, 32, 44, 45, 46]  # Work relationship
    v = [33, 34, 35, 36, 37, 38, 39, 40]  # Violence
    # Sum of each category, domain and final answer
    category = [0, 0, 0, 0, 0]
    domain = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    final_answer = 0
    val_str = ["Siempre", "Casi siempre", "Algunas veces", "Casi nunca", "Nunca"]
    inv_val_str = ["Nunca", "Casi nunca", "Algunas veces", "Casi siempre", "Siempre"]
    # Get the sum of all the answers in each domain
    for section in survey.sections.all():
        for question in section.questions.all():
            question_str = str(question.id)
            try:
                value = int(request.POST.get(question_str, 0))
            except ValueError:
                continue
            if question.number < 0:
                if value == 0:
                    content = "No"
                else:
                    content = "Si"
            elif question.inverted:
                content = inv_val_str[value]
            else:
                content = val_str[value]
            if question.number in wec:
                domain[0] += value
            elif question.number in wl:
                domain[1] += value
            elif question.number in wlc:
                domain[2] += value
            elif question.number in wd:
                domain[3] += value
            elif question.number in fwr:
                domain[4] += value
            elif question.number in l:
                domain[5] += value
            elif question.number in wr:
                domain[6] += value
            elif question.number in v:
                domain[7] += value

            Answer.objects.create(
                answer_sheet=answer_sheet,
                question=question,
                value=value,
                content=content,
            )
    # Work environment
    category[0] = domain[0]
    # Activity factor
    category[1] = domain[1] + domain[2]
    # Time organization
    category[2] = domain[3] + domain[4]
    # Leadership relationship
    category[3] = domain[5] + domain[6] + domain[7]
    # Final answer
    final_answer = sum(category[:5])
    return domain, category, final_answer


def grade_guide_III(request, survey, answer_sheet):
    wec = [1, 2, 3, 4, 5]  # Work environment conditions
    wl = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 65, 66, 67, 68]  # Working load
    wlc = [23, 24, 25, 26, 27, 28, 29, 30, 35, 36]  # Work lack control
    wd = [17, 18]  # Working day
    fwr = [19, 20, 21, 22]  # Family work relationship
    l = [31, 32, 33, 34, 37, 38, 39, 40, 41]  # Leadership
    wr = [42, 43, 44, 45, 46, 69, 70, 71, 72]  # Work relationship
    v = [57, 58, 59, 60, 61, 62, 63, 64]  # Violence
    pr = [47, 48, 49, 50, 51, 52]  # Performance recognition
    sbi = [53, 54, 55, 56]  # Sense belonging instability
    # Sum of each category, domain and final answer
    category = [0, 0, 0, 0, 0]
    domain = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    final_answer = 0
    val_str = ["Siempre", "Casi siempre", "Algunas veces", "Casi nunca", "Nunca"]
    inv_val_str = ["Nunca", "Casi nunca", "Algunas veces", "Casi siempre", "Siempre"]
    # Get the sum of all the answers in each domain
    for section in survey.sections.all():
        for question in section.questions.all():
            question_str = str(question.id)
            try:
                value = int(request.POST.get(question_str, 0))
            except KeyError:
                continue
            if question.number < 0:
                if value == 0:
                    content = "No"
                else:
                    content = "Si"
            elif question.inverted:
                content = inv_val_str[value]
            else:
                content = val_str[value]
            if question.number in wec:
                domain[0] += value
            elif question.number in wl:
                domain[1] += value
            elif question.number in wlc:
                domain[2] += value
            elif question.number in wd:
                domain[3] += value
            elif question.number in fwr:
                domain[4] += value
            elif question.number in l:
                domain[5] += value
            elif question.number in wr:
                domain[6] += value
            elif question.number in v:
                domain[7] += value

            Answer.objects.create(
                answer_sheet=answer_sheet,
                question=question,
                value=value,
                content=content,
            )
    # Work environment
    category[0] = domain[0]
    # Activity factor
    category[1] = domain[1] + domain[2]
    # Time organization
    category[2] = domain[3] + domain[4]
    # Leadership relationship
    category[3] = domain[5] + domain[6] + domain[7]
    # Organizational environment
    category[3] = domain[8] + domain[9]
    # Final answer
    final_answer = sum(category[:5])
    return domain, category, final_answer


def value_to_text_II(domain, category, final_answer):
    for i in range(len(domain)):
        if i == 0:
            domain[i] = text_options(domain[i], 3, 5, 7, 9)
        elif i == 1:
            domain[i] = text_options(domain[i], 12, 16, 20, 24)
        elif i == 2 or i == 6:
            domain[i] = text_options(domain[i], 5, 8, 11, 14)
        elif i == 3 or i == 4:
            domain[i] = text_options(domain[i], 1, 2, 4, 6)
        elif i == 5:
            domain[i] = text_options(domain[i], 3, 5, 8, 11)
        elif i == 7:
            domain[i] = text_options(domain[i], 7, 10, 13, 16)

    for i in range(len(category)):
        if i == 0:
            category[i] = text_options(category[i], 3, 5, 7, 9)
        elif i == 1:
            category[i] = text_options(category[i], 10, 20, 30, 40)
        elif i == 2:
            category[i] = text_options(category[i], 4, 6, 9, 12)
        elif i == 3:
            category[i] = text_options(category[i], 10, 18, 28, 38)

        # Final answer
    final_answer = text_options(final_answer, 20, 45, 70, 90)

    return domain, category, final_answer


def value_to_text_III(domain, category, final_answer):
    for i in range(len(domain)):
        if i == 0:
            domain[i] = text_options(domain[i], 5, 9, 11, 14)
        elif i == 1:
            domain[i] = text_options(domain[i], 15, 21, 27, 37)
        elif i == 2:
            domain[i] = text_options(domain[i], 11, 16, 21, 25)
        elif i == 3:
            domain[i] = text_options(domain[i], 1, 2, 4, 6)
        elif i == 4 or i == 9:
            domain[i] = text_options(domain[i], 4, 6, 8, 10)
        elif i == 5:
            domain[i] = text_options(domain[i], 9, 12, 16, 20)
        elif i == 6:
            domain[i] = text_options(domain[i], 10, 13, 17, 21)
        elif i == 7:
            domain[i] = text_options(domain[i], 7, 10, 13, 16)
        elif i == 8:
            domain[i] = text_options(domain[i], 6, 10, 14, 18)

    for i in range(len(category)):
        if i == 0:
            category[i] = text_options(category[i], 5, 9, 11, 14)
        elif i == 1:
            category[i] = text_options(category[i], 15, 30, 45, 60)
        elif i == 2:
            category[i] = text_options(category[i], 5, 7, 10, 13)
        elif i == 3:
            category[i] = text_options(category[i], 14, 29, 42, 58)
        elif i == 4:
            category[i] = text_options(category[i], 10, 14, 18, 23)

        # Final answer
    final_answer = text_options(final_answer, 50, 75, 99, 140)

    return domain, category, final_answer


def text_options(value, nulo, bajo, medio, alto):
    if value < nulo:
        return "Nulo"
    elif value < bajo:
        return "Bajo"
    elif value < medio:
        return "Medio"
    elif value < alto:
        return "Alto"
    return "Muy alto"


def download_surveys(request, survey_id):
    company = is_company(request.user)
    try:
        if request.user.is_authenticated and company is not None:
            survey = company.surveys.get(id=survey_id)
            sheets = AnswerSheet.objects.filter(survey=survey)
        data = {}
        for sheet in sheets:
            data[sheet.employee] = {}
            for answer in sheet.answers.all():
                data[sheet.employee][answer.question.content] = answer.content
        df = pd.DataFrame(data)
        filename = f"Nom035_Guia_{survey.guide_number}.csv"
        # To use temporary files uncomment next line and replace filename to filename.name whenever its used
        # filename = NamedTemporaryFile(suffix='.csv')
        df.to_csv(filename)
        chunk_size = 8192
        response = StreamingHttpResponse(
            FileWrapper(open(filename, "rb"), chunk_size),
            content_type=mimetypes.guess_type(filename)[0],
        )
        response["Content-Length"] = os.path.getsize(filename)
        response["Content-Disposition"] = f"Attachment;filename={filename}"
        return response
    except Survey.DoesNotExist:
        return redirect(_404(request, "Page not found", "404.html"))
