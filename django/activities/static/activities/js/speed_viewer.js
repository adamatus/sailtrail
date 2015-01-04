/* FIXME Conversion from m/s to knots is currently hard coded into file! */

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

	drawplot: function(spds) {
		var width = $('#speed-plot').width(),
			  height = $('#speed-plot').height(),
				margins = [40, 40, 10, 10],
				mb = margins[0], ml = margins[1], mt = margins[2], mr = margins[3],
				w = width - (ml + mr),
				h = height - (mb + mt),
				line = this.d3.svg.line(),
				time_format = this.d3.time.format('%Y-%m-%dT%X+00:00'),
				xAxis,
				yAxis,
				that = this;

		this.speeds = spds.map(function(d) { return d.speed; });
		this.times = spds.map(function(d) { return time_format.parse(d.time); });

		this.x = this.d3.time.scale().range([0, w]).domain([this.d3.min(this.times),
																									this.d3.max(this.times)]);
		xAxis = this.d3.svg.axis().scale(this.x).ticks(6).orient('bottom');
		this.y = this.d3.scale.linear().range([h, 0]).domain([0, this.d3.max(this.speeds)]);
		yAxis = this.d3.svg.axis().scale(this.y).ticks(4).orient('left');

		var svg = this.d3.select('#speed-plot')
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
			.attr('x', w/2)
			.attr('y', h+32)
			.text('Time');

		this.plot.append('g')
			.attr('class', 'y axis')
			.call(yAxis);

		this.plot.append("text")
		    .attr('class', 'y label')
				.attr('text-anchor', 'middle')
				.attr('transform', 'translate(-32,'+(h/2)+') rotate(-90)')
				.text('Speed (' + units.speed + ')');

		line.x(function(d) { return that.x(time_format.parse(d.time)); })	
			  .y(function(d) { return that.y(d.speed); });

		this.plot.append('svg:path')
			.attr('d', line(spds))
			.style('stroke', 'black')
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
