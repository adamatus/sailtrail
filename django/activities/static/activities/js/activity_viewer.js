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
    data: undefined,
    max_speed: undefined,
    units: undefined,
    urls: undefined,
    do_track: true,
    do_speed: true,
    do_polars: true,
    do_slider: true,

    /**
     * Initialize all the parts of an activity page asynchronously
     *
     * @param {Object} urls The URLs to fetch the data from
     * @param {Number} max_speed Precomputed max speed, used for axis max
     * @param {Number} wind_direction The current wind-direction estimate
     * @param {Object} units Object holding the current unit details
     * @param {Object} config Optional config object
     */
    init: function(urls, max_speed, wind_direction, units, config) {
        this.max_speed = max_speed;
        this.units = units;
        this.wind_direction = wind_direction;
        this.urls = urls;
        if (config) {
            this.do_track = config.do_track || true;
            this.do_speed = config.do_speed || true;
            this.do_polars = config.do_polars || true;
            this.do_slider = config.do_slider || true;
        }

        d3.json(urls.json, this.setup.bind(this));
    },

    /**
     * Create the individual pieces (plots/maps/sliders) after
     * the data has been fetched
     *
     * @param {Object} error
     * @param {Object} data The data response from the async server fetch
     */
    setup: function(error, data) {
        this.data = data;

        if (this.do_slider) {
            this.time_slider = $('#time-slider');
            this.setup_slider();
            this.setup_trim_events();
        }
        if (this.do_track) {
            track_viewer.draw_map(this.data, this.max_speed, this.time_slider);
        }
        if (this.do_speed) {
            speed_viewer.draw_plot(this.data, this.max_speed, this.units, this.time_slider);
        }
        if (this.do_polars) {
            polar_viewer.draw_plot(this.data, this.wind_direction, this.time_slider, this.urls.winddir);
        }
    },

    /**
     * Setup the timepoint slider
     */
    setup_slider: function() {
        var self = this;

        this.time_slider.slider({
            max: this.data.time.length,
            value: 0,
            formatter: function(value) {
                if (value < 0) {
                    return self.data.time[0];
                } else if (value >= self.data.time.length) {
                    return self.data.time[self.data.time.length - 1];
                }
                return self.data.time[value];
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
            $('#input-trim-start').val(self.data.time[new_val]);
        });

        $('#trim-end').on('click', function trim_end() {
            var new_val = self.time_slider.slider('getValue');

            // Save selected value to hidden input field
            $('#input-trim-end').val(self.data.time[new_val]);
        });
    },
};

module.exports = activity_viewer;

window.activity_viewer = activity_viewer;
