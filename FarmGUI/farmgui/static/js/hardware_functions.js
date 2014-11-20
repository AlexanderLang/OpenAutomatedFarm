
function edit_periphery_controller (response) {
    // dismiss modal dialog (if there was no error)
    if (response.error == false){
        $('#edit_periphery_controller_modal_'+response.periphery_controller.id).modal('hide');
        // edit name
        $('#periphery_controller_name_'+response.periphery_controller.id).text(response.periphery_controller.name);
    }
    // insert form again
    var modal_body = $('#edit_periphery_controller_modal_'+response.periphery_controller.id).find('.modal-body');
    modal_body.append(response.form);
    if (response.error == true){
        modal_body.prepend(response.error_msg);
    }

    deform.processCallbacks();
}

function remove_periphery_controller(pc_id) {
    $.ajax({url : '/hardware/pc/delete/'+pc_id}).done(function(data){
        if(data.delete == true){
            $('#delete_periphery_controller_modal_'+pc_id).modal('hide');
            $('#periphery_controller_panel_'+pc_id).remove();
        }
	});
}