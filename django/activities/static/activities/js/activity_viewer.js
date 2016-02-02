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
    trim_slider: undefined,
    data: undefined,
    max_speed: undefined,
    units: undefined,
    urls: undefined,
    do_track: true,
    do_speed: true,
    do_polars: true,
    do_slider: true,
    do_trim_slider: false,
    config: undefined,

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
        this.config = config;
        this.max_speed = max_speed;
        this.units = units;
        this.wind_direction = wind_direction;
        this.urls = urls;
        if (config) {
            this.do_track = config.do_track !== undefined ? config.do_track : true;
            this.do_speed = config.do_speed !== undefined ? config.do_speed : true;
            this.do_polars = config.do_polars !== undefined ? config.do_polars : true;
            this.do_slider = config.do_slider !== undefined ? config.do_slider : true;
            this.do_trim_slider = config.do_trim_slider !== undefined ? config.do_trim_slider : true;
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
        }
        if (this.do_trim_slider) {
            this.config.trim_start_index = data.time.indexOf(this.config.trim_start);
            this.config.trim_end_index = data.time.indexOf(this.config.trim_end);
            this.trim_slider = $('#trim-slider');
            this.setup_trim_slider();
        }
        if (this.do_track) {
            track_viewer.draw_map(this.data, this.max_speed, this.time_slider, this.trim_slider, this.config);
        }
        if (this.do_speed) {
            speed_viewer.draw_plot(this.data, this.max_speed, this.units, this.time_slider, this.trim_slider, this.config);
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
            max: this.data.time.length - 1,
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
                    .slider('setValue', new_val, true);

                evnt.preventDefault();
            }
        });
    },

    /**
     * Setup the trimming slider
     */
    setup_trim_slider: function() {
        var self = this;

        this.trim_slider.slider({
            max: this.data.time.length - 1,
            range: true,
            value: [this.config.trim_start_index || 0,
                    this.config.trim_end_index || this.data.time.length - 1],
            tooltip_split: true,
            formatter: function(value) {
                if (value < 0) {
                    return self.data.time[0];
                } else if (value >= self.data.time.length) {
                    return self.data.time[self.data.time.length - 1];
                }
                return self.data.time[value];
            },
        });

        this.trim_slider.on('slide', function(event) {
            $('#input-trim-start').val(self.data.time[event.value[0]]);
            $('#input-trim-end').val(self.data.time[event.value[1]]);
        });

        $(window).on('keydown', function handle_trim_scrolling(evnt) {
            var cur_val,
                lower_val,
                upper_val;

            if ($.inArray(evnt.keyCode, [37, 39, 38, 40]) >= 0) {
                cur_val = self.trim_slider.slider('getValue');
                lower_val = cur_val[0];
                upper_val = cur_val[1];

                if (evnt.keyCode === 37) { // Left arrow
                    lower_val = lower_val - 1;
                }
                if (evnt.keyCode === 39) { // Right arrow
                    lower_val = lower_val + 1;
                }
                if (evnt.keyCode === 40) { // Down arrow
                    upper_val = upper_val - 1;
                }
                if (evnt.keyCode === 38) { // Up arrow
                    upper_val = upper_val + 1;
                }
                self.trim_slider
                    .slider('setValue', [lower_val, upper_val], true);

                evnt.preventDefault();
            }
        });
    },
};

module.exports = activity_viewer;

window.activity_viewer = activity_viewer;
