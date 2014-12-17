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

function edit_device_link(response) {
    // dismiss modal dialog (if there was no error)
    if (response.error == false) {
        $('#edit_device_link_modal_' + response.device_link.id).modal('hide');
        // append new component to list
        $('#device_link_name_' + response.device_link.id).text(response.device_link_name);
    }
    // insert form again
    var modal_body = $('#edit_device_link_modal_' + response.device_link.id).find('.modal-body');
    modal_body.append(response.form);
    if (response.error == true) {
        modal_body.prepend(response.error_msg);
    }

    deform.processCallbacks();
}


function add_parameter_link(response) {
    // dismiss modal dialog (if there was no error)
    if (response.error == false) {
        $('#add_parameter_link_modal_' + response.parameter_link.display_id).modal('hide');
        // append new parameter to list
        var param_link_list = $('#parameter_link_list_' + response.parameter_link.display_id);
        param_link_list.append("<div class=\"panel_container\">" + response.parameter_link_panel + "</div>");
    }
    // insert form again
    $('#add_parameter_link_modal_' + response.parameter_link.display_id).find('.modal-body').append(response.form);

    deform.processCallbacks();
}


function add_device_link(response) {
    // dismiss modal dialog (if there was no error)
    if (response.error == false) {
        $('#add_device_link_modal_' + response.device_link.display_id).modal('hide');
        // append new parameter to list
        var device_link_list = $('#device_link_list_' + response.device_link.display_id);
        device_link_list.append("<div class=\"panel_container\">" + response.device_link_panel + "</div>");
    }
    // insert form again
    $('#add_device_link_modal_' + response.device_link.display_id).find('.modal-body').append(response.form);

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

function remove_device_link(device_link_id) {
    $.ajax({url: '/display/device_link/delete/' + device_link_id}).done(function (data) {
        if (data.delete == true) {
            $('#delete_device_link_modal_' + device_link_id).modal('hide');
            $('#device_link_panel_' + device_link_id).remove();
        }
    });
}

$(document).ready(
    function () {
        var now = new Date();
        var xmin = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate());

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
                timezone: "browser"
            }
        };
        var log_diagram_ids = [];
        var data_series = [];
        var plots = [];

        function get_log_diagram_ids () {
            $.each($("[id^='plot_placeholder_']"), function(index, container){
                log_diagram_ids.push(container.id.split('_').pop());
            });
        }
        get_log_diagram_ids();

        function initialize_data_series(diagram_ids) {
            for (var i = 0; i < diagram_ids.length; i++) {
                var log_diagram_series = [];
                var pl_list = $("#parameter_link_list_" + diagram_ids[i]);
                var dl_list = $("#device_link_list_" + diagram_ids[i]);
                $.each(pl_list.find("[id^='parameter_link_panel_']"), function (index, container) {
                    log_diagram_series.push({
                        label: $(container).data("link_name"),
                        data: [],
                        color: $(container).data("color")
                    });
                });
                $.each(dl_list.find("[id^='device_link_panel_']"), function (index, container) {
                    log_diagram_series.push({
                        label: $(container).data("link_name"),
                        data: [],
                        color: $(container).data("color")
                    });
                });
                data_series.push(log_diagram_series);
            }
        }
        initialize_data_series(log_diagram_ids);

        function initialize_plots(diagram_ids) {
            for (var i = 0; i < diagram_ids.length; i++) {
                var placeholder = $('#plot_placeholder_'+diagram_ids[i]);
                var plot = placeholder.plot(data_series[i], initial_plot_options).data("plot");
                plots.push(plot);
            }
        }
        initialize_plots(log_diagram_ids);

        function get_parameter_links(display_id) {
            var results = [];
            var links = $("#display_"+display_id).find("[id^='parameter_link_panel_']");
            for (var i = 0; i < links.length; i++) {
                results.push($(links[i]).data("parameter_id") + ' ' + $(links[i]).data("target"));
            }
            return results;
        }

        function get_device_links(display_id) {
            var results = [];
            var links = $("#display_"+display_id).find("[id^='device_link_panel_']");
            for (var i = 0; i < links.length; i++) {
                results.push($(links[i]).data("device_id") + ' ' + $(links[i]).data("target"));
            }
            return results;
        }

        function update_plot(index, log_diagram_id, data) {
            var plot = plots[index];
            var series = data_series[index];
            var panel = $('#display_'+log_diagram_id);
            var period = panel.data('period');
            var now = new Date();
            //console.log('now:   '+now);
            var starttime = now.getTime() - period * 1000;
            //var st = new Date(starttime);
            for (var i = 0; i < data.data.length; i++) {
                var new_points = data.data[i].data;
                var data_label = data.data[i].label;
                // find line with matching label
                var line;
                for(var j = 0; j < series.length; j++){
                    line = series[j];
                    if (line.label == data_label){
                        break;
                    }
                }
                // remove logs that are too old
                if (line.data.length>0) {
                    //console.log('removing older than: '+st.toString());
                    var lst = new Date(line.data[0][0]);
                    //console.log('checking:            '+lst.toString());
                    while(line.data[0][0]< starttime){
                        //console.log('removing one...')
                        line.data.shift();
                    }
                }
                for(var j = 0; j < new_points.length; j++){
                    line.data.push(new_points[j]);
                }
            }
            plot.setData(series);
            plot.setupGrid();
            plot.draw();
            var interval = 5000;
            setTimeout(function () {
                get_log_diagram_data(index, log_diagram_id, interval/1000);
            }, interval);
        }

        function get_log_diagram_data(index, log_diagram_id, period) {
            var post_data = {
                'parameter_links': get_parameter_links(log_diagram_id),
                'device_links': get_device_links(log_diagram_id),
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
            var panel = $('#display_'+log_diagram_ids[i]);
            var period = panel.data('period');
            get_log_diagram_data(i, log_diagram_ids[i], period);
        }
    });