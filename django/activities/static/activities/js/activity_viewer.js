'use strict';

var d3 = require('d3'),
    $ = require('jquery');

var speed_viewer = require('./speed_viewer'),
    track_viewer = require('./track_viewer'),
    polar_viewer = require('./polar_viewer');

var activity_viewer;

require('seiyria-bootstrap-slider');

activity_viewer = {
    time_slider: undefined,
    pos: undefined,
    max_speed: undefined,
    units: undefined,

    /**
     * Initialize all the parts of an activity page asynchronously
     *
     * @param {String} pos_url The URL to fetch the data from
     * @param {Number} max_speed Precomputed max speed, used for axis max
     * @param {Object} units Object holding the current unit details
     */
    init: function(pos_url, max_speed, units) {
        this.max_speed = max_speed;
        this.units = units;
        d3.json(pos_url, this.setup.bind(this));
    },

    /**
     * Create the individual pieces (plots/maps/sliders) after
     * the data has been fetched
     *
     * @param {Object} error
     * @param {Object} data The data response from the async server fetch
     */
    setup: function(error, data) {
        this.pos = data.details;
        this.time_slider = $('#time-slider');
        this.setup_slider();
        track_viewer.draw_map(this.pos, this.max_speed, this.time_slider);
        speed_viewer.draw_plot(this.pos, this.max_speed, this.units, this.time_slider);
        polar_viewer.draw_plot(this.pos, data.polars, this.time_slider);
        this.setup_trim_events();
    },

    /**
     * Setup the timepoint slider
     */
    setup_slider: function() {
        var self = this;

        this.time_slider.slider({
            max: this.pos.length,
            value: 0,
            formatter: function(value) {
                if (value < 0) {
                    return self.pos[0].time;
                } else if (value >= self.pos.length) {
                    return self.pos[self.pos.length - 1].time;
                }
                return self.pos[value].time;
            },
        });

        $(window).on('keydown', function handle_trim_scrolling(evnt) {
            var new_val;

            if ($.inArray(evnt.keyCode, [37, 39]) >= 0) {
                if (evnt.keyCode === 37) { // Left arrow
                    new_val = self.time_slider.slider('getValue') - 1;
                }
                if (evnt.keyCode === 39) { // Right arrow
                    new_val = self.time_slider.slider('getValue') + 1;
                }
                self.time_slider
                    .slider('setValue', new_val)
                    .trigger('slide', [new_val]);
            }
        });
    },

    /**
     * Setup the event handlers for trimming the timeseries data
     */
    setup_trim_events: function() {
        var self = this;

        $('#trim-start').on('click', function trim_start() {
            var new_val = self.time_slider.slider('getValue');

            // Save selected value to hidden input field
            $('#input-trim-start').val(self.pos[new_val].time);
        });

        $('#trim-end').on('click', function trim_end() {
            var new_val = self.time_slider.slider('getValue');

            // Save selected value to hidden input field
            $('#input-trim-end').val(self.pos[new_val].time);
        });
    },
};

module.exports = activity_viewer;

window.activity_viewer = activity_viewer;
