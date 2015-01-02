/* FIXME Conversion from m/s to knots is currently hard coded into file! */

module.exports = {
	speeds: [],
	times: [],
	plot: undefined,
	marker: undefined,
	x: undefined,
	y: undefined,

	drawplot: function(spds) {
		var width = $('#speed-plot').width(),
			  height = $('#speed-plot').height(),
				margins = [40, 40, 10, 10],
				mb = margins[0], ml = margins[1], mt = margins[2], mr = margins[3],
				w = width - (ml + mr),
				h = height - (mb + mt),
				line = d3.svg.line(),
				time_format = d3.time.format('%Y-%m-%dT%X+00:00'),
				xAxis,
				yAxis,
				that = this;

		this.speeds = spds.map(function(d) { return d.speed; });
		this.times = spds.map(function(d) { return time_format.parse(d.time); });

		this.x = d3.time.scale().range([0, w]).domain([d3.min(this.times),
																									d3.max(this.times)]);
		xAxis = d3.svg.axis().scale(this.x).ticks(6).orient('bottom');
		this.y = d3.scale.linear().range([h, 0]).domain([0, d3.max(this.speeds)]);
		yAxis = d3.svg.axis().scale(this.y).ticks(4).orient('left');

		var svg = d3.select('#speed-plot')
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
			.attr('cx', this.x(this.times[0]))
			.attr('cy', this.y(this.speeds[0]))
			.style('fill', 'black')
			.style('stroke', 'black')
			.style('stroke-width', 3);
	},

	movemarker: function(i) {
		if ((i >= 0) && (i < this.speeds.length)) {
			this.marker
				.attr('cx', this.x(this.times[i]))
				.attr('cy', this.y(this.speeds[i]));
		}
	},
};
