

function plot_data(data){
	var test = [ [ 0, 3 ], [ 4, 8 ], [ 8, 5 ], [ 9, 13 ] ];
	$.plot($("#placeholder"), data, {
		xaxis: {mode: "time",
			timeformat: "%H:%M",
			min: 0,
			max: 86400000}});
}

function get_configurations_data(stage_id){
	$.getJSON("/plant_settings/stages/"+stage_id+"/configurations_data",
			function (data) {
		plot_data(data.data);
	});
}