'use strict';

var $ = require('jquery'),
    d3 = require('d3');

var deg2rad = function(bearing) {
    return bearing * Math.PI / 180;
};

module.exports = {
    polars: undefined,
    plot: undefined,
    marker: undefined,
    x: undefined,
    y: undefined,
    marker_pos: 0,
    manual_offset: 0,
    mode: 'actual',
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
     * @param {Array.<Object>} spds Array of timepoints with speed info
     * @param {Number} max_speed Precomputed max speed, used for axis max
     * @param {Object} units Object holding the current unit details
     */
    draw_plot: function(pos, polars) {
        var width = $('#polar-plot').width(),
            height = $('#polar-plot').height(),
            radius = Math.min(width, height) / 2 - 30,
            self = this,
            maxes,
            len,
            mid,
            svg, gr, ga,
            temp_speeds,
            alignments = [],
            diffs, i, j;

        this.pos = pos;

        maxes = polars.map(function get_max(d) { return d.max; });

        this.max_r = d3.max(maxes);
        this.bearings = pos.map(function get_bearing(d) { return d.bearing; });
        this.speeds = pos.map(function get_speed(d) { return d.speed; });

        this.pol_speeds = polars.map(function get_mean(d) { return d.mean; });
        this.pol_bearings = polars.map(function get_bearing(d) { return d.bearing; });

        len = this.pol_speeds.length;
        mid = len / 2;
        temp_speeds = this.pol_speeds.slice();

        // Attempt to guess where the breeze is coming from by finding the
        // min around the polar plot.  This is very naive and will need
        // improvement
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

        // Angle axis
        ga = this.plot.append('g')
                .attr('class', 'a axis')
                .selectAll('g')
                    .data(d3.range(0, 360, 30))
                .enter().append('g')
                    .attr('transform', function rotate(d) { return 'rotate(' + self.bearing_to_css_rot(d) + ')'; });

        ga.append('line')
            .attr('x2', radius);

        ga.append('text')
            .attr('x', radius + 6)
                .attr('dy', '.35em')
                .style('text-anchor', function get_text_anchor(d) { return d > 180 ? 'end' : null; })
                .attr('transform', function get_text_transform(d) { return d > 180 ? 'rotate(180 ' + (radius + 6) + ',0)' : null; })
                .text(function get_x_text(d) { return d + '°'; });

        this.polar_g = this.plot.append('g')
            .on('click', function trigger_toggle() {
                self.toggle_mode();
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
        this.wind = this.polar_g.append('svg:line')
            .attr('x2', this.r(d3.max(this.pol_speeds)))
            .attr('class', 'polar wind')
            .attr('transform', 'rotate(' + self.bearing_to_css_rot(this.wind_offset) + ')');

        $(window).on('keydown', function adjust_estimated_wind_dir(evnt) {
            if ($.inArray(evnt.keyCode, [38, 40]) >= 0) {
                if (evnt.keyCode === 38) { // Up arrow
                    self.wind_offset++;
                } else { // Down arrow
                    self.wind_offset--;
                }
                evnt.preventDefault();
                $('#manual-wind-dir').val(self.wind_offset);
                self.update_rotation();
            }
        });

        $('#manual-wind-dir').on('keyup input', function() {
            self.wind_offset = $('#manual-wind-dir').val();
            self.update_rotation();
        });

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
     * Toggle the orientation of the polar plot from actual direction to wind at top
     */
    toggle_mode: function() {
        var data, i;

        if (this.mode === 'actual') {
            // Switch label to relative to wind
            data = d3.range(0, 181, 30);

            for (i = 5; i; i--) {
                data.push(data[i]);
            }
            d3.selectAll('.a.axis text')
                    .data(data)
                .text(function(d) { return d + '°'; });
            this.mode = 'polar';
        } else {
            // Switch labels to cardinals
            d3.selectAll('.a.axis text')
                    .data(d3.range(0, 360, 30))
                .text(function(d) { return d + '°'; });
            this.mode = 'actual';
        }
        this.update_rotation();
    },

    update_rotation: function() {
        this.wind.attr('transform', 'rotate(' + this.bearing_to_css_rot(this.wind_offset) + ')');
        if (this.mode === 'actual') {
            this.polar_g.transition().attr('transform', 'rotate(0)');
        } else {
            this.polar_g.transition().attr('transform', 'rotate(' + this.bearing_to_css_rot(90 - this.wind_offset) + ')');
        }
    },
};
