$(document).ready(function() {
	if ($('#add_component_modal').attr('data-add-component-error') == 'True') {
		$('#add_component_modal').modal({
			show : true
		});
	}
});