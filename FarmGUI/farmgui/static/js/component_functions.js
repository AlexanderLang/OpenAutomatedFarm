
function edit_component (response) {
    // dismiss modal dialog (if there was no error)
    if (response.error == false){
        $('#edit_component_modal_'+response.component.id).modal('hide');
        // append new component to list
        $('#component_name_'+response.component.id).text(response.component.name);
        $('#component_description_'+response.component.id).text(response.component.description);
    }
    // insert form again
    var modal_body = $('#edit_component_modal_'+response.component.id).find('.modal-body');
    modal_body.append(response.form);
    if (response.error == true){
        modal_body.prepend(response.error_msg);
    }

    deform.processCallbacks();
}

function edit_component_input (response) {
    // dismiss modal dialog (if there was no error)
    if (response.error == false){
        $('#edit_component_input_modal_'+response.component_input.id).modal('hide');
        $('#component_input_connected_output_'+response.component_input.id).text(response.connected_output_name);
        if (response.component_input.connected_output != null) {
            var redis_val = $('#ci_' + response.component_input.id + '_redis_value');
            redis_val.attr('data-redis', response.component_input.redis_key);
        } else {
            $('#ci_' + response.component_input.id + '_redis_value').attr('data-redis', 'nc');
        }
    }
    // insert form again
    var modal_body = $('#edit_component_input_modal_'+response.component_input.id).find('.modal-body');
    modal_body.append(response.form);
    if (response.error == true){
        modal_body.prepend(response.error_msg);
    }

    deform.processCallbacks();
}

function edit_component_property(response) {
    // dismiss modal dialog (if there was no error)
    if(response.error == false) {
        $('#edit_component_property_modal_'+response.component_property.id).modal('hide');
        $('#component_property_value_'+response.component_property.id).text(response.component_property.value)
    }
    // insert form again
    var modal_body = $('#edit_component_property_modal_'+response.component_property.id).find('.modal-body');
    modal_body.append(response.form);
    if (response.error == true){
        modal_body.prepend(response.error_msg);
    }

    deform.processCallbacks();
}

function remove_component(comp_id) {
    $.ajax({url : '/components/delete/'+comp_id}).done(function(data){
        if(data.delete == true){
            $('#delete_component_modal_'+comp_id).modal('hide');
            $('#component_'+comp_id).remove();
        }
	});
}

function add_parameter (response) {
    // dismiss modal dialog (if there was no error)
    if (response.error == false){
        $('#add_parameter_modal').modal('hide');
        // append new parameter to list
        var param_list = $('#parameter_list');
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