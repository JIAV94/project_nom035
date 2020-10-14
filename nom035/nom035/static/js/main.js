$(document).ready(function () {

  // Register and Update employee password validation
  $('.employeeForm').submit(function (e) {
    e.preventDefault();
    let password, confirmPassword, submitBtn, msg;
    if (this.id === "registerEmployee") {
      password = $('#password').val();
      confirmPassword = $('#password_confirmation').val();
      submitBtn = $('#register-submit-btn')[0];
      msg = "Las contraseñas deben coincidir para poder registrar al empleado.";
    }
    else if (this.id === "updateEmployee") {
      password = $('#update_password').val();
      confirmPassword = $('#update_password_confirmation').val();
      submitBtn = $('#update-submit-btn')[0];
      msg = "Las contraseñas deben coincidir para poder actualizar al empleado.";
    }
    if (password === confirmPassword) {
      this.submit();
    }
    else {
      alert(msg);
      submitBtn.disabled = false;
    }
  });

  // Fill Update employee modal
  $('.ed-emp').click(function () {
    employee_id = $(this).data('employeeId');
    action_url = $('#updateEmployee').attr('action')
    action_url = action_url.substring(0, action_url.lastIndexOf("/")) + '/' + employee_id;
    $('#updateEmployee').attr('action', action_url)
    $('#updateEmployeeModal').modal('show');
    $.ajax({
      type: 'GET',
      url: '/user/employees/retrieve/' + employee_id,
      success: function (employee_data) {
        $('#update_first_name').val(employee_data[0].first_name);
        $('#update_last_name').val(employee_data[0].last_name);
        $('#update_email').val(employee_data[0].email);
        $('#update_birthdate').val(employee_data[0].birthdate);
        $('#update_civil_status').val(employee_data[0].civil_status);
        $('#update_educational_level').val(employee_data[0].educational_level);
        $('#update_position').val(employee_data[0].position);
        $('#update_area').val(employee_data[0].area);
        $('#update_position_type').val(employee_data[0].position_type);
        $('#update_contract_type').val(employee_data[0].contract_type);
        $('#update_personnel_type').val(employee_data[0].personnel_type);
        $('#update_working_day_type').val(employee_data[0].working_day_type);
        employee_data[0].shift_rotation ?
          $('input:radio[name="shift_rotation"]').filter('[value="1"]').attr('checked', true) :
          $('input:radio[name="shift_rotation"]').filter('[value="0"]').attr('checked', true);
        $('#update_current_position_time').val(employee_data[0].current_position_time);
        $('#update_work_experience_time').val(employee_data[0].work_experience_time);
      }
    })
  });

  // Switch password update
  $('#changePassword').change(function (e) {
    if (e.target.checked) {
      $('#div_password').removeAttr('hidden');
      $('#div_password_confirmation').removeAttr('hidden');
    } else {
      $('#div_password').attr('hidden', true);
      $('#div_password_confirmation').attr('hidden', true);
      $('#update_password').val('');
      $('#update_password_confirmation').val('');
    }
  })

  // Delete employee
  $('.del-emp').click(function () {
    employee_id = $(this).data('employeeId');
    employee_name = $(this).data('employeeName');
    action_url = $('#deleteEmployee').attr('action')
    action_url = action_url.substring(0, action_url.lastIndexOf("/")) + '/' + employee_id;
    $('#deleteEmployee').attr('action', action_url);
    $('#deleteModalName').replaceWith("<strong>" + employee_name + "</strong>");
    $('#deleteEmployeeModal').modal('show');
  });

  // Fill Update survey modal
  $('.ed-surv').click(function () {
    survey_id = $(this).data('surveyId');
    action_url = $('#updateSurvey').attr('action')
    action_url = action_url.substring(0, action_url.lastIndexOf("/")) + '/' + survey_id;
    $('#updateSurvey').attr('action', action_url)
    $('#updateSurveyModal').modal('show');
    $.ajax({
      type: 'GET',
      url: '/surveys/retrieve/' + survey_id,
      success: function (survey_data) {
        $('#update_responsible').val(survey_data[0].responsible);
        $('#update_responsible_id').val(survey_data[0].responsible_id);
        $('#update_conclusions').val(survey_data[0].conclusions);
        $('#update_method').val(survey_data[0].method);
        $('#update_objective').val(survey_data[0].objective);
        $('#update_recommendations').val(survey_data[0].recommendations);
        $('#update_main_activities').val(survey_data[0].main_activities);
      }
    })
  });

  // Delete survey
  $('.del-surv').click(function () {
    survey_id = $(this).data('surveyId');
    survey_title = $(this).data('surveyTitle');
    action_url = $('#deleteSurvey').attr('action')
    action_url = action_url.substring(0, action_url.lastIndexOf("/")) + '/' + survey_id;
    $('#deleteSurvey').attr('action', action_url);
    $('#deleteModalTitle').replaceWith("<strong>" + survey_title + "</strong>");
    $('#deleteSurveyModal').modal('show');
  });

  // Hide questions from section -1 depending on the answer
  $('#survey-switch-1 :input').change(function () {
    if ($('#survey-switch-1 > div > input').first().is(':checked')) {
      $('.section-hidden').attr('hidden', false)
      $('.question-hidden').attr('hidden', false)
      $('.question-hidden :input').attr('required', true)
    }
    else {
      $('.section-hidden').attr('hidden', true)
      $('.question-hidden').attr('hidden', true)
      $('.question-hidden :input').attr('required', false).prop('checked', false)
    }
  });

  // Hide questions from section -2 depending on the answer
  $('#survey-switch-2 :input').change(function () {
    if ($('#survey-switch-2 > div > input').first().is(':checked')) {
      $('.question-hidden-2').attr('hidden', false)
      $('.question-hidden-2 :input').attr('required', true)
    }
    else {
      $('.question-hidden-2').attr('hidden', true)
      $('.question-hidden-2 :input').attr('required', false).prop('checked', false)
    }
  });

  // Index view graphs
  if (document.getElementById("guide_II_III_chart")) {
    const ctx = document.getElementById("guide_II_III_chart")
    const guide_II_III_chart = new Chart(ctx, {
      type: 'polarArea',
      data: {
        datasets: [{
          data: [
            ctx.dataset.graphNulo,
            ctx.dataset.graphBajo,
            ctx.dataset.graphMedio,
            ctx.dataset.graphAlto,
            ctx.dataset.graphMuyAlto
          ],
          backgroundColor: ['#58A1D9', '#B0D8A4', '#FEE191', '#FD8060', '#E84258'],
          hoverBackgroundColor: ['#2e59d9', '#17a673', '#ffe42e', '#F24F09', '#E42024'],
          hoverBorderColor: "rgba(234, 236, 244, 1)",

        }],
        labels: ["Nulo", "Bajo", "Medio", "Alto", "Muy Alto"],
      },
      options: {
        maintainAspectRatio: false,
        legend: {
          display: true
        },
        cutoutPercentage: 30,
      },
    });
  }
  else if (document.getElementById("guide_I_chart")) {
    const ctx = document.getElementById("guide_I_chart");
    const guide_I_chart = new Chart(ctx, {
      type: 'pie',
      data: {
        datasets: [{
          data: [
            ctx.dataset.graphNo,
            ctx.dataset.graphSi
          ],
          backgroundColor: ['#58A1D9', '#E84258'],
          hoverBackgroundColor: ['#2e59d9', '#E42024'],
          hoverBorderColor: "rgba(234, 236, 244, 1)",

        }],
        labels: ["No Requiere Atención", "Requiere Atencion"],
      },
      options: {
        maintainAspectRatio: false,
        legend: {
          display: true
        },
        cutoutPercentage: 30,
      },
    });
  }
});