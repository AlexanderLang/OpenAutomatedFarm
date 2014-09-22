$(document).ready(function() {
	if ($('#add_component_modal').attr('data-add-component-error') == 'True') {
		$('#add_component_modal').modal({
			show : true
		});
	}
});

function add_component (rText, sText, xhr, form) {
    // dismiss modal dialog (if there was no error)
    if (rText.error == false){
        $('#add_component_modal').modal('hide');
        // append new component to list
        $('#component_list').append(rText.component);
    }
    // insert form again
    var modal_body = $('#add_component_modal').find('.modal-body')
    modal_body.append(rText.form);
    if (rText.error == true){
        modal_body.prepend(rText.error_msg);
    }

    deform.processCallbacks();
}

function edit_component (rText, sText, xhr, form) {
    // dismiss modal dialog (if there was no error)
    if (rText.error == false){
        $('#edit_component_modal_'+rText.component._id).modal('hide');
        // append new component to list
        $('#component_name_'+rText.component._id).text(rText.component.name);
    }
    // insert form again
    var modal_body = $('#edit_component_modal_'+rText.component._id).find('.modal-body')
    modal_body.append(rText.form);
    if (rText.error == true){
        modal_body.prepend(rText.error_msg);
    }

    deform.processCallbacks();
}

function add_parameter (rText, sText, xhr, form) {
    // dismiss modal dialog (if there was no error)
    if (rText.error == false){
        $('#add_parameter_modal_'+rText.comp_id).modal('hide');
        // append new parameter to list
        var param_list = $('#parameter_list_'+rText.comp_id);
        param_list.append("<div class=\"col-sm-4 panel_container\">" + rText.parameter_panel + "</div>");
    }
    // insert form again
    $('#add_parameter_modal_'+rText.comp_id).find('.modal-body').append(rText.form);

    deform.processCallbacks();
}

function edit_parameter (rText, sText, xhr, form) {
    // dismiss modal dialog (if there was no error)
    if (rText.error == false){
        $('#edit_parameter_modal_'+rText.parameter._id).modal('hide');
        // replace name
        $('#parameter_name_'+rText.parameter._id).text(rText.parameter.name);
        $('#parameter_description_'+rText.parameter._id).text(rText.parameter.description);
        $('#parameter_type_'+rText.parameter._id).text(rText.parameter.parameter_type.name + " [" + rText.parameter.parameter_type.unit + "]");
        $('#parameter_sensor_'+rText.parameter._id).text(rText.parameter.sensor.periphery_controller.name + "-->" + rText.parameter.sensor.name);
        $('#parameter_interval_'+rText.parameter._id).text(rText.parameter.interval);
    }
    // insert form again
    $('#edit_parameter_modal_'+rText.parameter._id).find('.modal-body').append(rText.form);

    deform.processCallbacks();
}

function add_device (rText, sText, xhr, form) {
    // dismiss modal dialog (if there was no error)
    if (rText.error == false){
        $('#add_device_modal_'+rText.comp_id).modal('hide');
        // append new device to list
        var dev_list = $('#device_list_'+rText.comp_id);
        dev_list.append("<div class=\"col-sm-4 panel_container\">" + rText.device_panel + "</div>");
    }
    // insert form again
    $('#add_device_modal_'+rText.comp_id).find('.modal-body').append(rText.form);

    deform.processCallbacks();
}

function edit_device (rText, sText, xhr, form) {
    // dismiss modal dialog (if there was no error)
    if (rText.error == false){
        $('#edit_device_modal_'+rText.device._id).modal('hide');
        // replace name
        $('#device_name_'+rText.device._id).text(rText.device.name);
        $('#device_description_'+rText.device._id).text(rText.device.description);
        $('#device_type_'+rText.device._id).text(rText.device.device_type);
        $('#device_actuator_'+rText.device._id).text(rText.device.actuator.periphery_controller.name + "-->" + rText.device.actuator.name);
    }
    // insert form again
    $('#edit_device_modal_'+rText.device._id).find('.modal-body').append(rText.form);

    deform.processCallbacks();
}

function add_regulator (rText, sText, xhr, form) {
    // dismiss modal dialog (if there was no error)
    if (rText.error == false){
        $('#add_regulator_modal_'+rText.comp_id).modal('hide');
        // append new regulator to list
        var reg_list = $('#regulator_list_'+rText.comp_id);
        reg_list.append("<div class=\"col-sm-4 panel_container\">" + rText.regulator_panel + "</div>");
    }
    // insert form again
    $('#add_regulator_modal_'+rText.comp_id).find('.modal-body').append(rText.form);

    deform.processCallbacks();
}

function edit_regulator (rText, sText, xhr, form) {
    // dismiss modal dialog (if there was no error)
    if (rText.error == false){
        $('#edit_regulator_modal_'+rText.regulator._id).modal('hide');
        // replace name
        $('#regulator_name_'+rText.regulator._id).text(rText.regulator.name);
        $('#regulator_description_'+rText.regulator._id).text(rText.regulator.description);
        $('#regulator_type_'+rText.regulator._id).text(rText.regulator.regulator_type.name);
        $('#regulator_input_parameter_'+rText.regulator._id).text(rText.regulator.input_parameter.name);
        $('#regulator_output_device_'+rText.regulator._id).text(rText.regulator.output_device.name);
    }
    // insert form again
    $('#edit_regulator_modal_'+rText.regulator._id).find('.modal-body').append(rText.form);

    deform.processCallbacks();
}