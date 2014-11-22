function add_log_diagram(response) {
    // dismiss modal dialog (if there was no error)
    if (response.error == false) {
        $('#add_log_diagram_modal').modal('hide');
        // append new parameter to list
        var param_list = $('#log_diagram_list');
        param_list.append("<div class=\"panel_container\">" + response.log_diagram_panel + "</div>");
    }
    // insert form again
    $('#add_log_diagram_modal').find('.modal-body').append(response.form);

    deform.processCallbacks();
}

function edit_log_diagram(response) {
    // dismiss modal dialog (if there was no error)
    if (response.error == false) {
        $('#edit_log_diagram_modal_' + response.log_diagram.id).modal('hide');
        // append new component to list
        $('#log_diagram_name_' + response.log_diagram.id).text(response.log_diagram.name);
        $('#log_diagram_description_' + response.log_diagram.id).text(response.log_diagram.description);
        $('#log_diagram_period_' + response.log_diagram.id).text('Period: ' + response.log_diagram.period);
    }
    // insert form again
    var modal_body = $('#edit_log_diagram_modal_' + response.log_diagram.id).find('.modal-body');
    modal_body.append(response.form);
    if (response.error == true) {
        modal_body.prepend(response.error_msg);
    }

    deform.processCallbacks();
}

function edit_parameter_link(response) {
    // dismiss modal dialog (if there was no error)
    if (response.error == false) {
        $('#edit_parameter_link_modal_' + response.parameter_link.id).modal('hide');
        // append new component to list
        $('#parameter_link_name_' + response.parameter_link.id).text(response.parameter_link_name);
    }
    // insert form again
    var modal_body = $('#edit_parameter_link_modal_' + response.parameter_link.id).find('.modal-body');
    modal_body.append(response.form);
    if (response.error == true) {
        modal_body.prepend(response.error_msg);
    }

    deform.processCallbacks();
}


function add_parameter_link(response) {
    // dismiss modal dialog (if there was no error)
    if (response.error == false) {
        $('#add_parameter_link_modal').modal('hide');
        // append new parameter to list
        var param_link_list = $('#parameter_link_list_' + response.parameter_link.display_id);
        param_link_list.append("<div class=\"panel_container\">" + response.parameter_link_panel + "</div>");
    }
    // insert form again
    $('#add_parameter_link_modal').find('.modal-body').append(response.form);

    deform.processCallbacks();
}

function remove_log_diagram(log_diagram_id) {
    $.ajax({url: '/display/log_diagram/delete/' + log_diagram_id}).done(function (data) {
        if (data.delete == true) {
            $('#delete_log_diagram_modal_' + log_diagram_id).modal('hide');
            $('#display_' + log_diagram_id).remove();
        }
    });
}

function remove_parameter_link(parameter_link_id) {
    $.ajax({url: '/display/parameter_link/delete/' + parameter_link_id}).done(function (data) {
        if (data.delete == true) {
            $('#delete_parameter_link_modal_' + parameter_link_id).modal('hide');
            $('#parameter_link_panel_' + parameter_link_id).remove();
        }
    });
}

$(document).ready(
    function () {

        var initial_plot_options = {
            series: {
                shadowSize: 0
                // Drawing is faster without shadows
            },
            yaxis: {
                min: 0,
                max: 100
            },
            xaxis: {
                mode: "time",
                timeformat: "%H:%M",
                min: 0,
                max: 86400000
            }
        };
        var log_diagram_ids = [];
        var plots = [];

        function get_log_diagram_ids () {
            $.each($("[id^='plot_placeholder_']"), function(index, container){
                log_diagram_ids.push(container.id.split('_').pop());
            });
        }
        get_log_diagram_ids();

        function initialize_plots(diagram_ids) {
            for (var i = 0; i < diagram_ids.length; i++) {
                var placeholder = $('#plot_placeholder_'+diagram_ids[i]);
                var plot = placeholder.plot([[0,0], [1,1]], initial_plot_options).data("plot");
                plots.push(plot);
            }
        }
        initialize_plots(log_diagram_ids);

        function get_parameter_ids(display_id) {
            var ids = [];
            var links = $("#display_"+display_id).find("[id^='parameter_link_panel_']");
            for (var i = 0; i < links.length; i++) {
                ids.push(links[i].getAttribute("data-parameter_id"));
            }
            return ids;
        }

        function update_plot(index, log_diagram_id, data) {
            var plot = plots[index];
            plot.setData(data.data);
            plot.getOptions().xaxes[0].min = data.xmin;
            plot.getOptions().xaxes[0].max = data.xmax;
            plot.setupGrid();
            plot.draw();
            var interval = 3000;
            setTimeout(function () {
                get_log_diagram_data(index, log_diagram_id);
            }, interval);
        }

        function get_log_diagram_data(index, log_diagram_id) {
            var panel = $('#display_'+log_diagram_id);
            var period = panel.data('period');
            var post_data = {
                'parameter_ids': get_parameter_ids(log_diagram_id),
                'plot_period': period};
            $.ajax({
                type: 'POST',
                url: '/display/log_diagram/data',
                data: post_data,
                traditional: true
            }).done(function (data) {
                update_plot(index, log_diagram_id, data);
            });
        }

        for(var i = 0; i < log_diagram_ids.length; i++){
            get_log_diagram_data(i, log_diagram_ids[i]);
        }
    });