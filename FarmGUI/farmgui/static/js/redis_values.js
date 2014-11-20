$(document).ready(
		function () {

		    get_redis_values();

			function update_redis_value(key, value) {
                $.each($("[data-redis="+key+"]"), function(index, container){
                    $(container).text(value);
                });
			}

			function update_redis_values(data) {
			    for (var key in data) {
			        update_redis_value(key, data[key]);
			    }
				var interval = 1000;
				setTimeout(function() {
				    get_redis_values()
				}, interval);
			}

			function get_redis_values() {
                var keys = [];
		        $.each($("[data-redis]"), function(index, value){
                    var val = $(value).attr("data-redis");
		            keys.push(val);
		        });
			    var post_data = {'keys': keys};
			    $.ajax({
			        type : 'POST',
			        url : '/redis_values',
			        data : post_data,
			        traditional : true
			    }).done(function(data){
			        update_redis_values(data);
			    });
			}
		});