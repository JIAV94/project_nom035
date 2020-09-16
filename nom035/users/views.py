from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import *
from django.http import JsonResponse
from .models import InformationLog, Employee
from surveys.models import AnswerSheet, Survey
from . import choices

# Finished
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index_view')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index_view')
        else:
            messages.error(request, 'El usuario o la contraseña son inconrrectos.')
            return redirect('login_view')
    else:
        return render(request,'login.html')

# Posible mejora
def user_logout(request):
    logout(request)
    return redirect('login_view')

# Finished
def index_view(request):
    if request.user.is_authenticated:
        employee = is_employee(request.user)
        company = is_company(request.user)
        surveys = []
        graph_data = None
        rca = None # Require clinical attention
        if company is not None:
            company = request.user.company
            surveys = company.surveys.order_by('-id')[:2]
            if surveys:
                rca, graph_data = company_index_data(surveys)
        else:
            employee = request.user.employee
            sheets = employee.answer_sheets.filter(final_answer="unanswered").order_by('-id')
            for sheet in sheets:
                surveys.append(sheet.survey)
        context = {
            'employee': employee,
            'company': company,
            'surveys': surveys,
            'graph_data': graph_data,
            'require_clinical_attention': rca
        }
        return render(request, 'users/index.html', context)
    else:
        return redirect('login_view')

# Finished
def register_employee(request):
    if request.method == 'POST':
        username = request.POST["username"]
        pwd = request.POST["password"]
        pwd_conf = request.POST["password_confirmation"]
        f_name = request.POST["first_name"]
        l_name = request.POST["last_name"]
        email = request.POST["email"]
        sex = request.POST["sex"]
        b_date = request.POST["birthdate"]
        civ_st = request.POST["civil_status"]
        educ_lvl = request.POST["educational_level"]
        pos = request.POST["position"]
        area = request.POST["area"]
        pos_type = request.POST["position_type"]
        contr_type = request.POST["contract_type"]
        pers_type = request.POST["personnel_type"]
        work_d_type = request.POST["working_day_type"]
        shft_rot = request.POST["shift_rotation"]
        curr_pos_t = request.POST["current_position_time"]
        work_exp_t = request.POST["work_experience_time"]

        company = is_company(request.user)
        if company is not None:
            employee_code = company.employees_code
            username = employee_code + username
        else:
            return redirect(_404(request, 'Page not found', '404.html'))
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe, prueba con otro')
            return redirect('user:employees_view')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'El email ingresado ya existe, prueba con otro')
            return redirect('user:employees_view')
        if pwd != pwd_conf and pwd != "":
            messages.error(request, 'Las contraseñas no coinciden')
            return redirect('user:employees_view')
        new_user = User.objects.create_user(
          username=username, email=email, password=pwd, 
          first_name=f_name, last_name=l_name)
        employee = Employee.objects.create(
          user=new_user, sex=sex, birthdate=b_date, company=company)
        InformationLog.objects.create(
          employee=employee, civil_status=civ_st, educational_level=educ_lvl,
          position=pos, area=area, position_type=pos_type,
          contract_type=contr_type, personnel_type=pers_type,
          working_day_type=work_d_type, shift_rotation=shft_rot,
          current_position_time=curr_pos_t, work_experience_time=work_exp_t)
    return redirect('user:employees_view')

# Finished
def update_employee(request, employee_id):
    if request.method == 'POST':
        f_name = request.POST["first_name"]
        l_name = request.POST["last_name"]
        email = request.POST["email"]
        pwd = request.POST["password"]
        pwd_conf = request.POST["password_confirmation"]
        b_date = request.POST["birthdate"]
        civ_st = request.POST["civil_status"]
        educ_lvl = request.POST["educational_level"]
        pos = request.POST["position"]
        area = request.POST["area"]
        pos_type = request.POST["position_type"]
        contr_type = request.POST["contract_type"]
        pers_type = request.POST["personnel_type"]
        work_d_type = request.POST["working_day_type"]
        shft_rot = request.POST["shift_rotation"]
        curr_pos_t = request.POST["current_position_time"]
        work_exp_t = request.POST["work_experience_time"]

        company = is_company(request.user)
        if company is not None:
            employee = get_object_or_404(Employee, id=employee_id)
            if employee.company == company:
                info = employee.information_logs.last()
            else:
                return redirect(_404(request, 'Page not found', '404.html'))
        else:
            return redirect(_404(request, 'Page not found', '404.html'))
        if pwd != "":
            if pwd != pwd_conf:
                messages.error(request, 'Las contraseñas no coinciden')
            else:
                valid_pwd = password_validation(pwd)
                if valid_pwd == 0:
                    employee.user.set_password(pwd)
                else:
                    messages.error(request, valid_pwd)
        if User.objects.filter(email=email).exists() and employee.user.email != email:
            messages.error(request, 'El email ingresado ya existe, prueba con otro')
        else:
            employee.user.email = email
        employee.birthdate = b_date
        employee.user.first_name = f_name
        employee.user.last_name = l_name
        employee.save()
        employee.user.save()
        InformationLog.objects.get_or_create(
              employee=employee, civil_status=civ_st, educational_level=educ_lvl,
              position=pos, area=area, position_type=pos_type,
              contract_type=contr_type, personnel_type=pers_type,
              working_day_type=work_d_type, shift_rotation=shft_rot,
              current_position_time=curr_pos_t, work_experience_time=work_exp_t)
    return redirect('user:employees_view')

# Finished
def load_employee_data(request, employee_id):
    if request.user.is_authenticated:
        company = is_company(request.user)
        if company is None:
            return redirect(_404(request, 'Page not found', '404.html'))
        employee = get_object_or_404(Employee, id=employee_id)
        information_log = employee.information_logs.last()
        if employee.company == company:
            employee = [{
              "first_name":employee.user.first_name, 
              "last_name":employee.user.last_name,
              "email":employee.user.email,
              "birthdate":employee.birthdate,
              "civil_status":information_log.civil_status,
              "educational_level":information_log.educational_level,
              "position":information_log.position,
              "area":information_log.area,
              "position_type":information_log.position_type,
              "contract_type":information_log.contract_type,
              "personnel_type":information_log.personnel_type,
              "working_day_type":information_log.working_day_type,
              "shift_rotation":information_log.shift_rotation,
              "current_position_time":information_log.current_position_time,
              "work_experience_time":information_log.work_experience_time
            }]
            return JsonResponse(employee, content_type='application/json', safe=False)
    return redirect('index_view')

# Finished
def password_validation(password):
    validators = [MinimumLengthValidator, CommonPasswordValidator, 
                  NumericPasswordValidator]
    try:
        for validator in validators:
            validator().validate(password)
        return 0
    except ValidationError as e:
        if str(e) == "['This password is too short. It must contain at least 8 characters.']":
            return "La contraseña es demasiado corta. Debe contener por lo menos 8 caracteres"
        elif str(e) == "['This password is too common.']":
            return "La contraseña es muy común."
        elif str(e) == "['This password is entirely numeric.']":
            return "La contraseña no puede ser enteramente numérica. Añade letras y símbolos."
        else:
            return str(e)

# Finished
def delete_employee(request, employee_id):
    company = is_company(request.user)
    if request.user.is_authenticated and company is not None:
        employee = get_object_or_404(Employee, id=employee_id)
        if employee.company == company:
            employee.user.delete()
            return redirect('user:employees_view')
    return redirect(_404(request, 'Page not found', '404.html'))

# Finished
def company_index_data(surveys):
    graph_data = []
    rca = surveys[0].answer_sheets.filter(final_answer="Requiere atención clínica")
    if surveys.count() == 1 or surveys[0].guide_number == surveys[1].guide_number:
        dnrca = surveys[0].answer_sheets.all().count()-rca.count()
        graph_data = [dnrca, rca.count()]
    else:
        graph_data.append(surveys[1].answer_sheets.filter(final_answer="Nulo").count())
        graph_data.append(surveys[1].answer_sheets.filter(final_answer="Bajo").count())
        graph_data.append(surveys[1].answer_sheets.filter(final_answer="Medio").count())
        graph_data.append(surveys[1].answer_sheets.filter(final_answer="Alto").count())
        graph_data.append(surveys[1].answer_sheets.filter(final_answer="Muy Alto").count())
    return rca, graph_data

# Finished
def employees_view(request):
    company = is_company(request.user)
    if request.user.is_authenticated and company is not None:
        try:
            employees = company.employees.all()
            guide_I = []
            guide_II = []
            for employee in employees:
                sheets = employee.answer_sheets.order_by('-id')[:2]
                if sheets:
                    if (sheets.count() == 1 or 
                        sheets[0].survey.guide_number == sheets[1].survey.guide_number):
                        guide_I.append(sheets[0].final_answer)
                        guide_II.append('NA')
                    elif sheets[0].survey.guide_number == 1:
                        guide_I.append(sheets[0].final_answer)
                        guide_II.append(sheets[1].final_answer)
                    else:
                        guide_I.append(sheets[1].final_answer)
                        guide_II.append(sheets[0].final_answer)
                else:
                    guide_I.append('N/A')
                    guide_II.append('N/A')
            employees_data = list(zip(employees, guide_I, guide_II))
            context = {
                'employees_data': employees_data,
                'civil_status': choices.civil_status,
                'educational_level': choices.educational_level,
                'position_type': choices.position_type,
                'contract_type': choices.contract_type,
                'personnel_type': choices.personnel_type,
                'working_day_type': choices.working_day_type,
                'current_position_time': choices.current_position_time,
                'work_experience_time': choices.work_experience_time,
            }
            return render(request, 'users/employee/employee_list.html', context)
        except:
            return redirect(_404(request, 'Page not found', '404.html'))
    else:
        return redirect(_404(request, 'Page not found', '404.html'))

# Finished
def employee_details_view(request, employee_id):
    company = is_company(request.user)
    if request.user.is_authenticated and company is not None:
        employee = get_object_or_404(Employee, id=employee_id)
        sheets = AnswerSheet.objects.filter(employee=employee).order_by('-id')
        info_log = employee.information_logs.last()
        context = {
          'employee': employee,
          'sheets': sheets,
          'info_log': info_log_string(info_log),
          'civil_status': choices.civil_status,
          'educational_level': choices.educational_level,
          'position_type': choices.position_type,
          'contract_type': choices.contract_type,
          'personnel_type': choices.personnel_type,
          'working_day_type': choices.working_day_type,
          'current_position_time': choices.current_position_time,
          'work_experience_time': choices.work_experience_time,
        }
        return render(request, 'users/employee/employee_details.html', context)
    return redirect(_404(request, 'Page not found', '404.html'))

# Finished
def info_log_string(info_log):
    info = {
      'civil_status': choices.civil_status[str(info_log.civil_status)],
      'educational_level':choices.educational_level[str(info_log.educational_level)],
      'position':info_log.position,
      'area':info_log.area,
      'position_type':choices.position_type[str(info_log.position_type)],
      'contract_type':choices.contract_type[str(info_log.contract_type)],
      'personnel_type':choices.personnel_type[str(info_log.personnel_type)],
      'working_day_type':choices.working_day_type[str(info_log.working_day_type)],
      'shift_rotation':info_log.shift_rotation,
      'current_position_time':choices.current_position_time[str(info_log.current_position_time)],
      'work_experience_time':choices.work_experience_time[str(info_log.work_experience_time)],
    }
    return info

# Finished
def policy_view(request):
    if request.method == 'POST':
        try:
            accept = request.POST['accept']
            employee = request.user.employee
            employee.policy = True
            employee.save()
            return redirect('index_view')
        except:
            messages.error(request,
                'Debes seleccionar la casilla inferior para concluir con tus encuestas.')
            return redirect('user:policy_view')
    else:
        return render(request, 'users/policy.html')

# Finished
def employee_answers_view(request, employee_id, survey_id):
    company = is_company(request.user)
    if request.user.is_authenticated and company is not None:
        survey = get_object_or_404(Survey, id=survey_id)
        employee = get_object_or_404(Employee, id=employee_id)
        if survey.company == employee.company and employee.company == company:
            answers_sheet = survey.answer_sheets.get(employee=employee)
            info_log = employee.information_logs.last()
            context = {
                'survey': survey,
                'employee': employee,
                'answers_sheet': answers_sheet,
                'info_log': info_log_string(info_log)
            }
            return render(request, 'users/employee/employee_answers.html', context)
        return redirect(_404(request, 'Page not found', '404.html'))
    return redirect('index_view')

# Finished
def is_company(user):
    try:
        company = user.company
        return company
    except:
        return None

# Finished
def is_employee(user):
    try:
        employee = user.employee
        return employee
    except:
        return None

# Finished
def _404(request, exception, template_name="404.html"):
    response = render_to_response(template_name)
    response.status_code = 404
    return response

# Finished
def _500(request, *args, **argv):
    return render(request, '404.html', status=500)
