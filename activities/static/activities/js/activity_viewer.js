var SpeedViewer = require('./speed_viewer'),
	  TrackViewer = require('./track_viewer');

$('#time-slider').slider({
	max: pos.length,
	value: 0,
	formatter: function(value) {
		if (value < 0) {
			return pos[0].time;
		} else if (value >= pos.length) {
			return pos[pos.length-1].time;
		} else {
			return pos[value].time;
		}
	}
});

TrackViewer.drawmap(pos);
SpeedViewer.drawplot(pos);

$('#time-slider').on('slide', function(slideEvt, data) {
		data = data | slideEvt.value;
		TrackViewer.movemarker(data);
		SpeedViewer.movemarker(data);
});

$(window).on('keydown', function(evnt) {
		var new_val;
		if ($.inArray(evnt.keyCode, [37, 39]) >= 0) {
			if (evnt.keyCode == 37) { // Left arrow
				new_val = $('#time-slider').slider('getValue') - 1;
			}
			if (evnt.keyCode == 39) { // Right arrow
				new_val = $('#time-slider').slider('getValue') + 1;
			}
			$('#time-slider')
				.slider('setValue', new_val)
				.trigger('slide', [new_val]);
		}
});

$('#trim-start').on('click', function(evnt) {
		var new_val = $('#time-slider').slider('getValue');
		$('#input-trim-start').val(pos[new_val].time);
});

$('#trim-end').on('click', function(evnt) {
		var new_val = $('#time-slider').slider('getValue');
		$('#input-trim-end').val(pos[new_val].time);
});
