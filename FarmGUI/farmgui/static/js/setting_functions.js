
function edit_field_setting (response) {
    // dismiss modal dialog (if there was no error)
    if (response.error == false){
        $('#edit_field_setting_modal_'+response.field_setting.name).modal('hide');
        // edit name
        $('#field_setting_value_'+response.field_setting.name).text(response.field_setting.value);
    }
    // insert form again
    var modal_body = $('#edit_field_setting_modal_'+response.field_setting.name).find('.modal-body');
    modal_body.append(response.form);
    if (response.error == true){
        modal_body.prepend(response.error_msg);
    }

    deform.processCallbacks();
}