$(document).ready(
		function() {
			var m_id = $("#measurement-title").attr("data-measurement-id");
			var plot = $.plot("#placeholder", [], {
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

			function update_plot(data) {
				plot.setData(data.data)
				plot.getOptions().xaxes[0].min = data.xmin;
				plot.getOptions().xaxes[0].max = data.xmax;
				plot.setupGrid();
				plot.draw();
				var interval = parseInt($("#interval").attr("data-interval"))*1000;
				setTimeout(function() {
					get_measurement_log_data(m_id)
				}, interval);
			}

			function get_measurement_log_data(measurement_id) {
				$.getJSON("/json/measurements/" + measurement_id
						+ "/logs", function(data) {
					update_plot(data);
				});
			}

			get_measurement_log_data(m_id);
		});