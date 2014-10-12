/* FIXME Conversion from m/s to knots is currently hard coded into file! */

var SpeedViewer = {
	speeds: [],
	plot: undefined,

	drawplot: function(spds) {
		var width = $('#speed-plot').width(),
			  height = $('#speed-plot').height(),
				margins = [40, 40, 10, 10],
				mb = margins[0], ml = margins[1], mt = margins[2], mr = margins[3];
				w = width - (ml + mr),
				h = height - (mb + mt),
				x = d3.scale.linear().range([0, w]).domain([0, spds.length]),
				xAxis = d3.svg.axis().scale(x).ticks(6).orient('bottom'),
				y = d3.scale.linear().range([h, 0]).domain([0, d3.max(spds)]),
				yAxis = d3.svg.axis().scale(y).ticks(4).orient('left'),
				line = d3.svg.line();

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
				.text('Speed (' + units['speed'] + ')');

		line.x(function(d,i) { return x(i); })	
			  .y(function(d) { return y(d); });

		this.plot.append('svg:path')
			.attr('d', line(spds))
			.style('stroke', 'black')
			.style('fill', 'none')
			.style('stroke-width', 2);

	},
};


