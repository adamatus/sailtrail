var $ = require('jquery');

module.exports = {
	d3: require('d3'),
	polars: undefined,
	plot: undefined,
	marker: undefined,
	x: undefined,
	y: undefined,
	marker_pos: 0,

	drawplot: function(pos, polars) {
		var width = $('#polar-plot').width(),
			  height = $('#polar-plot').height(),
				radius = Math.min(width, height)/2 - 30,
				that = this;

		this.maxes = polars.map(function(d) { return d.max; });

		this.max_r = d3.max(this.maxes);
		this.bearings = pos.map(function(d) { return d.bearing; });
		this.speeds = pos.map(function(d) { return d.speed; });


		this.r = d3.scale.linear()
			.domain([0, this.max_r*1.2])
			.range([0, radius]);

		this.mean_line = d3.svg.line.radial()
			.radius(function(d) { return that.r(d.mean); })
			.angle(function(d) { return Math.PI/180 * (-d.bearing); });

		this.max_line = d3.svg.line.radial()
			.radius(function(d) { return that.r(d.max); })
			.angle(function(d) { return Math.PI/180 * (-d.bearing); });

		var svg = this.d3.select('#polar-plot')
			.append('svg:svg')
			  .attr('id', 'polar-plot-svg')
				.attr('width', width)
				.attr('height', height);

		this.plot = svg.append('g')
			.attr('transform', 'translate(' + width/2 + ',' + height/2 + ')');

		// Radius axis
		var gr = this.plot.append("g")
				.attr("class", "r axis")
			.selectAll("g")
				.data(this.r.ticks(5).slice(1))
			.enter().append("g");

		gr.append("circle")
		    .attr("r", this.r);

		gr.append("text")
				.attr("y", function(d) { return -that.r(d) - 4; })
				.attr("transform", "rotate(15)")
				.style("text-anchor", "middle")
				.text(function(d) { return d; });

		// Angle axis
		var ga = this.plot.append("g")
				.attr("class", "a axis")
				.selectAll("g")
					.data(d3.range(0, 360, 30))
				.enter().append("g")
					.attr("transform", function(d) { return "rotate(" + (d-90) + ")"; });

		ga.append("line")
		    .attr("x2", radius);

		ga.append("text")
		    .attr("x", radius + 6)
				.attr("dy", ".35em")
				.style("text-anchor", function(d) { return d > 180 ? "end" : null; })
				.attr("transform", function(d) { return d > 180 ? "rotate(180 " + (radius + 6) + ",0)" : null; })
				.text(function(d) { return d + "°"; });

		// The mean line
		this.plot.append("path")
			.datum(polars)
			.attr("class", "polar mean")
			.attr("d", this.mean_line);

		// The mean line
		this.plot.append("path")
			.datum(polars)
			.attr("class", "polar max")
			.attr("d", this.max_line);

		// The current bearing line
		this.marker = this.plot.append('svg:line')
			.attr('x2', this.r(this.speeds[this.marker_pos]))
			.attr("class", "polar bearing")
			.attr("transform", "rotate(" + (-(this.bearings[this.marker_pos]+90)) + ")");

	},

	movemarker: function(i) {
		this.marker_pos = (i < 0) ? 0 : (i >= this.speeds.length) ? this.speeds.length - 1 : i;
		this.marker
			.attr('x2', this.r(this.speeds[this.marker_pos]))
			.attr("transform", "rotate(" + (-(this.bearings[this.marker_pos]+90)) + ")");
	},

};
