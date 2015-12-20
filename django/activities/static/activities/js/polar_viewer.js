'use strict';

var $ = require('jquery'),
    _ = require('lodash'),
    cookies = require('cookies-js'),
    d3 = require('d3');

var deg2rad = function(bearing) {
    return bearing * Math.PI / 180;
};

module.exports = {
    polars: undefined,
    plot: undefined,
    marker: undefined,
    winddir_url: undefined,
    x: undefined,
    y: undefined,
    marker_pos: 0,
    manual_offset: 0,
    pos: undefined,

    bearing_to_css_rot: function(bearing) {
        return bearing - 90;
    },

    bearing_to_d3_rot: function(bearing) {
        return deg2rad(bearing);
    },

    /**
     * Main function to initialize plot
     *
     * @param {Object} data Arrays of track info
     * @param {Integer} wind_direction
     * @param {Element} time_slider The time_slider element
     * @param {String} winddir_url The url of this activites wind direction endpoint
     */
    draw_plot: function(data, wind_direction, time_slider, winddir_url) {
        var width = $('#polar-plot').width(),
            height = $('#polar-plot').height(),
            radius = Math.min(width, height) / 2 - 30,
            self = this,
            maxes,
            len,
            mid,
            r_scale_step,
            r_end,
            polars = [],
            pos = [],
            svg, gr, ga,
            temp_speeds,
            alignments = [],
            window_size = 6, // Polar plot bin size
            diffs, i, j;

        this.data = data;
        this.winddir_url = winddir_url;

        // Compute polars (inefficiently for now)

        // Reshape data into old, array of objects format for now
        _.forEach(data.bearing, function(time, k) {
            pos.push({speed: data.speed[k], bearing: data.bearing[k]});
        });

        // Bin the individual trackpoints into bearing bins
        this.groups = _.groupBy(pos, function bin_bearings(d) {
            return (Math.round(d.bearing / window_size)
                    * window_size + (window_size / 2)) % 360;
        });

        this.pol_speeds = [];
        this.pol_bearings = d3.range(window_size / 2, 360, window_size);

        // Compute summary stats for the bins
        this.pol_bearings.forEach(function(d) {
            var bearing = d.toString(),
                group,
                speeds,
                mean;

            if (self.groups[bearing] && self.groups[bearing].length) {
                group = self.groups[bearing];
                speeds = _.map(group, function(point) { return point.speed; });
                speeds = _.filter(speeds, function(point) { return point > 0.5; });
                mean = d3.mean(speeds) || 0;
                self.pol_speeds.push(mean);
                polars.push({
                    bearing: d,
                    max: d3.max(speeds) || 0,
                    median: d3.median(speeds) || 0,
                    mean: mean,
                    measurements: group.length,
                    points: _.map(group, function(point) { return _.pick(point, ['bearing', 'speed']); }),
                });
            } else {
                self.pol_speeds.push(0);
                polars.push({bearing: d, max: 0, median: 0, mean: 0, measurements: 0, points: []});
            }
        });

        maxes = polars.map(function get_max(d) { return d.max; });

        this.max_r = d3.max(maxes);
        this.bearings = data.bearing;
        this.speeds = data.speed;

        if (wind_direction === null) {
            // Attempt to guess where the breeze is coming from by finding the
            // min around the polar plot.  This is very naive and will need
            // improvement
            len = this.pol_speeds.length;
            mid = len / 2;
            temp_speeds = this.pol_speeds.slice();

            for (j = 0; j < len; j++) {
                if (j > 0) {
                    temp_speeds.push(temp_speeds.shift());
                }
                diffs = [];
                for (i = 0; i < mid; i++) {
                    diffs.push(temp_speeds[i] - temp_speeds[len - i - 1]);
                }
                alignments.push(Math.abs(d3.sum(diffs)));
            }
            this.wind_offset = this.pol_bearings[alignments.indexOf(d3.min(alignments))];
            $('#manual-wind-dir').val(this.wind_offset);
        } else {
            this.wind_offset = wind_direction;
            // $('#manual-wind-dir').val(this.wind_offset);
        }

        // Create the scale for the radius of the polar plot,
        // setting it to be a little larger than the max speed
        this.r = d3.scale.linear()
            .domain([0, this.max_r * 1.2])
            .range([0, radius]);

        this.mean_line = d3.svg.line.radial()
            .radius(function get_radial_mean(d) { return self.r(d.mean); })
            .interpolate('cardinal-closed')
            .angle(function get_radial_bearing(d) { return self.bearing_to_d3_rot(d.bearing); });

        this.max_line = d3.svg.line.radial()
            .radius(function get_radial_max(d) { return self.r(d.max); })
            .interpolate('cardinal-closed')
            .angle(function get_radial_bearing(d) { return self.bearing_to_d3_rot(d.bearing); });

        svg = d3.select('#polar-plot')
            .append('svg:svg')
              .attr('id', 'polar-plot-svg')
                .attr('width', width)
                .attr('height', height);

        this.plot = svg.append('g')
            .attr('transform', 'translate(' + width / 2 + ',' + height / 2 + ')');

        // Radius axis
        gr = this.plot.append('g')
                .attr('class', 'r axis')
            .selectAll('g')
                .data(this.r.ticks(5).slice(1))
            .enter().append('g');

        gr.append('circle')
            .attr('r', this.r);

        gr.append('text')
                .attr('y', function offset_r_text(d) { return -self.r(d) - 4; })
                .attr('transform', 'rotate(15)')
                .style('text-anchor', 'middle')
                .text(function get_r_text(d) { return d; });

        self.dir_map = {};
        self.dir_map['0'] = 'N';
        self.dir_map['45'] = 'NE';
        self.dir_map['90'] = 'E';
        self.dir_map['135'] = 'SE';
        self.dir_map['180'] = 'S';
        self.dir_map['225'] = 'SW';
        self.dir_map['270'] = 'W';
        self.dir_map['315'] = 'NW';

        // Angle axis
        ga = this.plot.append('g')
                .attr('class', 'a axis')
                .selectAll('g')
                    .data(d3.range(0, 360, 45))
                .enter().append('g')
                    .attr('transform', function rotate(d) { return 'rotate(' + self.bearing_to_css_rot(d) + ')'; });

        ga.append('line')
            .attr('x2', radius);

        ga.append('text')
            .attr('x', radius + 6)
                .attr('dy', '.35em')
                .style('text-anchor', function get_text_anchor(d) { return d > 180 ? 'end' : null; })
                .attr('transform', function get_text_transform(d) { return d > 180 ? 'rotate(180 ' + (radius + 6) + ',0)' : null; })
                .text(function get_x_text(d) { return self.dir_map[d.toString()]; });

        this.polar_g = this.plot.append('g')
            .on('click', function trigger_toggle() {
                $('#polar-frame-of-ref').bootstrapToggle('toggle');
            });

        // The mean line
        this.polar_g.append('path')
            .datum(polars)
            .attr('class', 'polar mean')
            .attr('d', this.mean_line);

        // The mean line
        this.polar_g.append('path')
            .datum(polars)
            .attr('class', 'polar max')
            .attr('d', this.max_line);

        // The current bearing line
        this.marker = this.polar_g.append('svg:line')
            .attr('x2', this.r(this.speeds[this.marker_pos]))
            .attr('class', 'polar bearing')
            .attr('transform', 'rotate(' + self.bearing_to_css_rot(this.bearings[this.marker_pos]) + ')');

        // The estimated wind direction
        this.wind = this.polar_g.append('svg:g')
            .attr('class', 'polar wind')
            .attr('transform', 'rotate(' + self.bearing_to_css_rot(this.wind_offset) + ')');

        r_scale_step = this.r.ticks(5).slice(this.r.ticks(5).length - 2);
        r_scale_step = r_scale_step[1] - r_scale_step[0];

        r_end = this.r.ticks(5).slice(this.r.ticks(5).length - 1)[0];

        this.wind.append('svg:line')
            .attr('x1', this.r(r_end + (3 * r_scale_step / 4)))
            .attr('x2', this.r(r_end - (3 * r_scale_step / 4)));

        this.wind.append('svg:line')
            .attr('y1', this.r(d3.max(this.pol_speeds) * 0.1))
            .attr('x1', this.r(r_end - (r_scale_step / 2)))
            .attr('x2', this.r(r_end - (3 * r_scale_step / 4)));

        this.wind.append('svg:line')
            .attr('y1', this.r(d3.max(this.pol_speeds) * -0.1))
            .attr('x1', this.r(r_end - (r_scale_step / 2)))
            .attr('x2', this.r(r_end - (3 * r_scale_step / 4)));

        // Only add the event listeners if the input is not disabled
        // (e.g., the owner is viewing the activity}
        if (!$('#manual-wind-dir').prop('disabled')) {
            $(window).on('keydown', function adjust_estimated_wind_dir(evnt) {
                if ($.inArray(evnt.keyCode, [38, 40]) >= 0) {
                    if (evnt.keyCode === 38) { // Up arrow
                        self.wind_offset = (self.wind_offset + 361) % 360;
                    } else { // Down arrow
                        self.wind_offset = (self.wind_offset + 359) % 360;
                    }
                    evnt.preventDefault();
                    $('#manual-wind-dir').val(self.wind_offset);
                    self.update_wind_dir_in_db();
                    self.update_rotation();
                }
            });
        }

        // Register with slider to update positional marker
        if (time_slider) {
            time_slider.on('slide', function movepolarmaker(slideEvnt, d) {
                var newdata = d | slideEvnt.value;

                self.move_marker(newdata);
            });
        }

        $('#manual-wind-dir').on('change', function() {
            self.wind_offset = $('#manual-wind-dir').val() % 360;
            $('#manual-wind-dir').val(self.wind_offset);
            self.update_wind_dir_in_db();
            self.update_rotation();
        });

        $('#polar-frame-of-ref').change(function() {
            self.toggle_mode();
        });

    },

    // This needs to quickly be replaced by a data-binding
    // with the db...
    update_wind_dir_in_db: function() {
        var self = this,
            csrftoken = cookies.get('csrftoken');

        clearTimeout(this.wait_to_post);
        self.wait_to_post = setTimeout(
            function() {
                $.post(self.winddir_url, { csrfmiddlewaretoken: csrftoken, wind_direction: self.wind_offset});
            },
            500
        );
    },

    /**
     * Move the polar marker to a new timepoint
     *
     * @param {Number} i The index in the polar array to move the marker to
     */
    move_marker: function(i) {
        this.marker_pos = (i < 0) ? 0 : (i >= this.speeds.length) ? this.speeds.length - 1 : i;
        this.marker
            .attr('x2', this.r(this.speeds[this.marker_pos]))
            .attr('transform', 'rotate(' + this.bearing_to_css_rot(this.bearings[this.marker_pos]) + ')');
    },

    /**
     * Toggle the orientation of the polar plot from actual direction to wind
     * at top
     */
    toggle_mode: function() {
        var toggle = $('#polar-frame-of-ref'),
            self = this,
            data, i;

        if (toggle.prop('checked')) {
            // Switch label to relative to wind
            data = d3.range(0, 181, 45);

            for (i = 3; i; i--) {
                data.push(data[i]);
            }
            d3.selectAll('.a.axis text')
                    .data(data)
                .text(function(d) { return d + '°'; });
        } else {
            // Switch labels to cardinals
            d3.selectAll('.a.axis text')
                    .data(d3.range(0, 360, 45))
                .text(function get_x_text(d) { return self.dir_map[d.toString()]; });
        }
        this.update_rotation();
    },

    update_rotation: function() {
        this.wind.attr('transform', 'rotate(' + this.bearing_to_css_rot(this.wind_offset) + ')');
        if (!$('#polar-frame-of-ref').prop('checked')) {
            this.polar_g.transition().attr('transform', 'rotate(0)');
        } else {
            this.polar_g.transition().attr('transform', 'rotate(' + this.bearing_to_css_rot(90 - this.wind_offset) + ')');
        }
    },
};
