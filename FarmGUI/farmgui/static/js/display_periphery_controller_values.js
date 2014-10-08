$(document).ready(
		function () {

		    var ids = [];
		    $.each($("[id^=periphery_controller_panel]"), function(index, value){
		        ids.push(value.getAttribute("data"));
		    });

		    for(var i = 0; i < ids.length; i++){
		        get_periphery_controller_values(ids[i]);
		    }

			function update_values(pc_id, data) {
                $.each(data, function(key, value){
                    $("#" + key).text(value);
                });
				var interval = 1000;
				setTimeout(function() {
					get_periphery_controller_values(pc_id)
				}, interval);
			}

			function get_periphery_controller_values(pc_id) {
			    $.ajax({url : '/display/periphery_controller/' + pc_id + '/values'}).done(function(data){
			        update_values(pc_id, data);
			    });
			}
		});