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
    $('#add_component_modal').find('.modal-body').append(rText.form);

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
    $('#edit_component_modal_'+rText.component._id).find('.modal-body').append(rText.form);

    deform.processCallbacks();
}

function add_parameter (rText, sText, xhr, form) {
    // dismiss modal dialog (if there was no error)
    if (rText.error == false){
        $('#add_parameter_modal_'+rText.comp_id).modal('hide');
        // append new component to list
        var param_list = $('#parameter_list_'+rText.comp_id);
        var container = param_list.find('div:first').clone();
        container.find('.panel_container:first').replaceWith(rText.parameter_panel);
        param_list.append(container);
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
    }
    // insert form again
    $('#edit_parameter_modal_'+rText.parameter._id).find('.modal-body').append(rText.form);

    deform.processCallbacks();
}