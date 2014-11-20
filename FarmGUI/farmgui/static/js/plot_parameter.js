$(document).ready(
		function () {
			var p_id = 1;
			var plot = $.plot("#plot-placeholder", [], {
				series : {
					shadowSize : 0
				// Drawing is faster without shadows
				},
				yaxis : {
					min : 0,
					max : 100
				},
				xaxis : {
					mode : "time",
					timeformat : "%H:%M",
					min : 0,
					max : 86400000
				}
			});

			function get_selected_parameter_ids(){
			    var ids = [];
			    var checkboxes = $("#plot-sidebar").find('input:checked');
			    for(var i = 0; i < checkboxes.length; i++){
			        ids.push(checkboxes[i].getAttribute("data"));
			    }
			    return ids;
			}

			function update_plot(data) {
				plot.setData(data.data);
				plot.getOptions().xaxes[0].min = data.xmin;
				plot.getOptions().xaxes[0].max = data.xmax;
				plot.setupGrid();
				plot.draw();
				var interval = 2000;
				setTimeout(function() {
					get_parameter_log_data(p_id)
				}, interval);
			}

			function get_parameter_log_data(parameter_ids) {
			    var post_data = {'parameter_ids': get_selected_parameter_ids(),
			                     'plot_period': $('input[name=plot_period]:checked').val()};
			    $.ajax({
			        type : 'POST',
			        url : '/display/parameter/data',
			        data : post_data,
			        traditional : true
			    }).done(function(data){
			        update_plot(data);
			    });
			}

			get_parameter_log_data(p_id);
		});