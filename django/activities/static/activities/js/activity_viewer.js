var SpeedViewer = require('./speed_viewer'),
	  TrackViewer = require('./track_viewer'),
		$ = require('jquery');

require('seiyria-bootstrap-slider');

var activity_viewer = {
	time_slider: undefined,
	pos: undefined,
	speed_viewer: SpeedViewer,
	track_viewer: TrackViewer,

	init: function(pos_url, max_speed) {
		var self = this;
		d3.json(pos_url, function(error, data) {
			self.pos = data;
			self.time_slider = $('#time-slider');
			self.setup_slider();
			self.track_viewer.drawmap(self.pos, max_speed);
			self.speed_viewer.drawplot(self.pos, max_speed);
			self.setup_trim_events();
		});
	},

	setup_slider: function() {
		var self = this;
		this.time_slider.slider({
			max: this.pos.length,
			value: 0,
			formatter: function(value) {
				if (value < 0) {
					return self.pos[0].time;
				} else if (value >= self.pos.length) {
					return self.pos[self.pos.length-1].time;
				} else {
					return self.pos[value].time;
				}
			}
		});

		this.time_slider.on('slide', function(slideEvt, data) {
				var newdata = data | slideEvt.value;
				TrackViewer.movemarker(newdata);
				SpeedViewer.movemarker(newdata);
		});
	},

	setup_trim_events: function() {
		var self = this;
		$(window).on('keydown', function(evnt) {
			var new_val;
			if ($.inArray(evnt.keyCode, [37, 39]) >= 0) {
				if (evnt.keyCode == 37) { // Left arrow
					new_val = self.time_slider.slider('getValue') - 1;
				}
				if (evnt.keyCode == 39) { // Right arrow
					new_val = self.time_slider.slider('getValue') + 1;
				}
				self.time_slider
					.slider('setValue', new_val)
					.trigger('slide', [new_val]);
			}
		});

		$('#trim-start').on('click', function(evnt) {
			// Save selected value to hidden input field
			var new_val = self.time_slider.slider('getValue');
			$('#input-trim-start').val(pos[new_val].time);
		});

		$('#trim-end').on('click', function(evnt) {
			// Save selected value to hidden input field
			var new_val = self.time_slider.slider('getValue');
			$('#input-trim-end').val(pos[new_val].time);
		});
	},
};

module.exports = activity_viewer;

window.activity_viewer = activity_viewer;
