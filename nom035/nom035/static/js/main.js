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

  // Oculta las preguntas de las encuestas dependiendo la respuesta
  $('#survey-switch-1 :input').change(function () {
    if ($('#survey-switch-1 > div > input').first().is(':checked')) {
      $('.section-hidden').attr('hidden', false)
      $('.question-hidden').attr('hidden', false)
      $('.question-hidden :input').attr('required', true)
    }
    else {
      $('.section-hidden').attr('hidden', true)
      $('.question-hidden').attr('hidden', true)
      $('.question-hidden :input').attr('required', false)
    }
  });

  // Oculta las preguntas de las encuestas dependiendo la respuesta
  $('#survey-switch-2 :input').change(function () {
    if ($('#survey-switch-2 > div > input').first().is(':checked')) {
      $('.question-hidden-2').attr('hidden', false)
      $('.question-hidden-2 :input').attr('required', true)
    }
    else {
      $('.question-hidden-2').attr('hidden', true)
      $('.question-hidden-2 :input').attr('required', false)
    }
  });
});