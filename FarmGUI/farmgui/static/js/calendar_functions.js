
function add_param_calendar_entry (response) {
    // dismiss modal dialog (if there was no error)
    if (response.error == false){
        $('#add_param_calendar_modal').modal('hide');
        // append new parameter to list
        var param_list = $('#param_calendar_list');
        param_list.append("<div class=\"col-sm-4 panel_container\">" + response.parameter_panel + "</div>");
    }
    // insert form again
    $('#add_parameter_modal').find('.modal-body').append(response.form);

    deform.processCallbacks();
}

function edit_parameter (response) {
    // dismiss modal dialog (if there was no error)
    if (response.error == false){
        // hide modal dialog
        $('#edit_parameter_modal_'+response.parameter.id).modal('hide');
        // replace sensor name
        if(response.parameter.sensor != null) {
            $('#parameter_sensor_name_' + response.parameter.id).text(response.sensor_name);
        } else {
            $('#parameter_sensor_name_' + response.parameter.id).text("No sensor selected");
        }
        // update output value
        edit_component_output(response.parameter);
    }
    // insert form again
    $('#edit_parameter_modal_'+response.parameter.id).find('.modal-body').append(response.form);

    deform.processCallbacks();
}

function edit_component_output(comp) {
    var component_selector = $('#component_output_panel_'+comp.id);
    var redis_val = component_selector.find('.redis_value');
    redis_val.attr('id', 'redis_value_'+comp.outputs.value.redis_key);
}

function add_device (response) {
    // dismiss modal dialog (if there was no error)
    if (response.error == false){
        $('#add_device_modal').modal('hide');
        // append new device to list
        var dev_list = $('#device_list');
        dev_list.append("<div class=\"col-sm-4 panel_container\">" + response.device_panel + "</div>");
    }
    // insert form again
    $('#add_device_modal').find('.modal-body').append(response.form);

    deform.processCallbacks();
}

function edit_device (response) {
    // dismiss modal dialog (if there was no error)
    if (response.error == false){
        $('#edit_device_modal_'+response.device.id).modal('hide');
        // replace sensor name
        if(response.device.actuator != null) {
            $('#device_actuator_name_' + response.device.id).text(response.actuator_name);
        } else {
            $('#device_actuator_name_' + response.device.id).text("No actuator selected");
        }
    }
    // insert form again
    $('#edit_device_modal_'+response.device.id).find('.modal-body').append(response.form);

    deform.processCallbacks();
}

function add_regulator (response) {
    // dismiss modal dialog (if there was no error)
    if (response.error == false){
        $('#add_regulator_modal').modal('hide');
        // append new regulator to list
        var reg_list = $('#regulator_list');
        reg_list.append("<div class=\"col-sm-4 panel_container\">" + response.regulator_panel + "</div>");
    }
    // insert form again
    $('#add_regulator_modal').find('.modal-body').append(response.form);

    deform.processCallbacks();
}

function edit_regulator (response) {
    // dismiss modal dialog (if there was no error)
    if (response.error == false){
        $('#edit_regulator_modal_'+response.regulator.id).modal('hide');
    } else {
    // insert form again
        $('#edit_regulator_modal_'+response.regulator.id).find('.modal-body').append(response.form);
    }
    deform.processCallbacks();

    if (response.error == false) {
        var reg_panel = $('#component_'+response.regulator.id);
        reg_panel.replaceWith(response.regulator_panel);
    }
}