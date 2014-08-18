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