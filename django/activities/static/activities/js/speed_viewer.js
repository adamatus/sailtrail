'use strict';

var $ = require('jquery');

module.exports = {
    d3: require('d3'),
    speeds: [],
    times: [],
    plot: undefined,
    marker: undefined,
    x: undefined,
    y: undefined,
    marker_pos: 0,

    drawplot: function(spds, max_speed, units) {
        var width = $('#speed-plot').width(),
            height = $('#speed-plot').height(),
            margins = [40, 40, 10, 10],
            mb = margins[0], ml = margins[1], mt = margins[2], mr = margins[3],
            w = width - (ml + mr),
            h = height - (mb + mt),
            line = this.d3.svg.line(),
            // FIXME Not handling timezones currently...
            time_format = this.d3.time.format('%Y-%m-%dT%X+0000'),
            svg,
            xAxis,
            yAxis,
            self = this;

        this.speeds = spds.map(function get_speed(d) { return d.speed; });
        this.times = spds.map(function get_parsed_time(d) { return time_format.parse(d.time); });

        this.x = this.d3.time.scale().range([0, w])
                     .domain([this.times[0], this.times[this.times.length - 1]]);
        xAxis = this.d3.svg.axis().scale(this.x).ticks(6).orient('bottom');
        this.y = this.d3.scale.linear().range([h, 0]).domain([0, max_speed]);
        yAxis = this.d3.svg.axis().scale(this.y).ticks(4).orient('left');

        svg = this.d3.select('#speed-plot')
                .append('svg:svg')
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

        line.x(function get_x_time(d) { return self.x(time_format.parse(d.time)); })
            .y(function get_y_speed(d) { return self.y(d.speed); });

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

        this.plot.append('svg:path')
            .attr('d', line(spds))
            .style('stroke', 'url(#speed-gradient)')
            .style('fill', 'none')
            .style('stroke-width', 2);

        this.marker = this.plot.append('svg:circle')
            .attr('r', 5)
            .attr('cx', this.x(this.times[this.marker_pos]))
            .attr('cy', this.y(this.speeds[this.marker_pos]))
            .style('fill', 'black')
            .style('stroke', 'black')
            .style('stroke-width', 3);
    },

    movemarker: function(i) {
        this.marker_pos = (i < 0) ? 0 : (i >= this.speeds.length) ? this.speeds.length - 1 : i;
        this.marker
            .attr('cx', this.x(this.times[this.marker_pos]))
            .attr('cy', this.y(this.speeds[this.marker_pos]));
    },
};
