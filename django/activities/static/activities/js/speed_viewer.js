'use strict';

var $ = require('jquery'),
    _ = require('lodash'),
    d3 = require('d3');

module.exports = {
    speeds: [],
    times: [],
    plot: undefined,
    marker: undefined,
    x: undefined,
    y: undefined,
    units: undefined,
    marker_pos: 0,

    /**
     * Main function to initialize plot
     *
     * @param {Object} data Object containing arrays with time and speed info
     * @param {Number} max_speed Precomputed max speed, used for axis max
     * @param {Object} units Object holding the current unit details
     * @param {Element} time_slider The time-slider to use
     */
    draw_plot: function(data, max_speed, units, time_slider) {
        var width = $('#speed-plot').width(),
            height = $('#speed-plot').height(),
            margins = [40, 40, 10, 10],
            mb = margins[0],
            ml = margins[1],
            mt = margins[2],
            mr = margins[3],
            w = width - (ml + mr),
            h = height - (mb + mt),
            time_format = d3.time.format('%Y-%m-%dT%X+0000'),
            svg,
            xAxis,
            yAxis,
            self = this;

        this.units = units;

        this.line_factory = d3.svg.line();

        this.speeds = data.speed;
        this.times = data.time.map(function get_parsed_time(d) { return time_format.parse(d); });

        this.x = d3.time.scale().range([0, w])
                     .domain([this.times[0], this.times[this.times.length - 1]]);
        xAxis = d3.svg.axis().scale(this.x).ticks(6).orient('bottom');
        this.y = d3.scale.linear().range([h, 0]).domain([0, max_speed]);
        yAxis = d3.svg.axis().scale(this.y).ticks(4).orient('left');

        svg = d3.select('#speed-plot').append('svg:svg')
            .attr('id', 'speed-plot-svg')
            .attr('width', width)
            .attr('height', height);

        this.plot = svg.append('g')
            .attr('transform', 'translate(' + ml + ',' + mt + ')');

        this.plot.append('g')
            .attr('class', 'x axis')
            .attr('transform', 'translate(0,' + h + ')')
            .call(xAxis);

        this.plot.append('text')
            .attr('class', 'x label')
            .attr('text-anchor', 'middle')
            .attr('x', w / 2)
            .attr('y', h + 32)
            .text('Time');

        this.plot.append('g')
            .attr('class', 'y axis')
            .call(yAxis);

        this.plot.append('text')
            .attr('class', 'y label')
            .attr('text-anchor', 'middle')
            .attr('transform', 'translate(-32,' + (h / 2) + ') rotate(-90)')
            .text('Speed (' + units.speed + ')');

        this.line_factory.x(function get_x_time(d) { return self.x(d[0]); })
                         .y(function get_y_speed(d) { return self.y(d[1]); });

        this.plot.append('linearGradient')
            .attr('id', 'speed-gradient')
            .attr('gradientUnits', 'userSpaceOnUse')
            .attr('x1', 0)
            .attr('x2', 0)
            .attr('y1', this.y(0))
            .attr('y2', this.y(this.y.domain()[1]))
            .selectAll('stop')
                    .data([
                        {offset: '0%', color: '#1a9850'},
                        {offset: '20%', color: '#91cf60'},
                        {offset: '40%', color: '#d9ef8b'},
                        {offset: '60%', color: '#fee08b'},
                        {offset: '80%', color: '#fc8d59'},
                        {offset: '100%', color: '#d73027'},
                    ])
                .enter().append('stop')
                    .attr('offset', function get_offset(d) { return d.offset; })
                    .attr('stop-color', function get_color(d) { return d.color; });

        this.base_line = this.plot.append('svg:path')
            .attr('id', 'speed-plot-base-line')
            .attr('d', this.line_factory(_.zip(this.times, this.speeds)))
            .style('stroke', '#BBB')
            .style('fill', 'none')
            .style('stroke-width', 1);

        this.colored_line = this.plot.append('svg:path')
            .attr('id', 'speed-plot-colored-line')
            .attr('d', this.line_factory(_.zip(this.times, this.speeds)))
            .style('stroke', 'url(#speed-gradient)')
            .style('fill', 'none')
            .style('stroke-width', 3);

        this.marker = this.plot.append('svg:circle')
            .attr('r', 5)
            .attr('cx', this.x(this.times[this.marker_pos]))
            .attr('cy', this.y(this.speeds[this.marker_pos]))
            .style('fill', 'black')
            .style('stroke', 'black')
            .style('stroke-width', 3);

        // Register with slider to update positional marker
        if (time_slider) {
            time_slider.on('slide', function movepolarmaker(slideEvnt, d) {
                var newdata = d || slideEvnt.value;

                self.move_marker(newdata);
            });
        }

        // Register with track-only-last-minute checkbox to optionally filter track
        this.filter_track = false;
        this.filter_state_changed = false;
        $('#track-only-last-minute').on('change', function(e) {
            self.filter_track = !!e.target.checked;
            self.filter_state_changed = true;
            self.update_plot();
        });
    },

    /**
     * Move the speed marker to a new timepoint
     *
     * @param {Number} i The index in the speed array to move the marker to
     */
    move_marker: function(i) {
        this.marker_pos = (i < 0) ? 0 : (i >= this.speeds.length) ? this.speeds.length - 1 : i;
        this.marker
            .attr('cx', this.x(this.times[this.marker_pos]))
            .attr('cy', this.y(this.speeds[this.marker_pos]));
        this.update_plot();
    },

    /**
     * Filter plot, based on current marker position
     */
    update_plot: function() {
        var self = this,
            data;

        if (this.filter_track) {
            data = _.zip(this.times, this.speeds);
            data = data.filter(function(d, i) {
                return (i <= self.marker_pos) && (i > (self.marker_pos - 60));
            });

            this.colored_line.attr('d', this.line_factory(data));
        } else if (this.filter_state_changed) {
            this.colored_line.attr('d', this.line_factory(_.zip(this.times, this.speeds)));
            this.filter_state_changed = false;
        }
    },
};
