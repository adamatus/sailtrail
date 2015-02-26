var $ = require('jquery');

module.exports = {
	d3: require('d3'),
	polars: undefined,
	plot: undefined,
	marker: undefined,
	x: undefined,
	y: undefined,
	marker_pos: 0,
	mode: 'actual',

	drawplot: function(pos, polars) {
		var width = $('#polar-plot').width(),
			  height = $('#polar-plot').height(),
				radius = Math.min(width, height)/2 - 30,
				that = this;

		this.maxes = polars.map(function(d) { return d.max; });

		this.max_r = d3.max(this.maxes);
		this.bearings = pos.map(function(d) { return d.bearing; });
		this.speeds = pos.map(function(d) { return d.speed; });

		this.pol_speeds = polars.map(function(d) { return d.mean; });
		this.pol_bearings = polars.map(function(d) { return d.bearing; });

		var len = this.pol_speeds.length,
			mid = len/2,
			temp_speeds = this.pol_speeds.slice(),
			alignments = [],
			diffs, i, j;

		for (j=0; j < len; j++) {
			if (j > 0) {
				temp_speeds.push(temp_speeds.shift());
			}
			diffs = [];
			for (i=0; i < mid; i++) {
				diffs.push(temp_speeds[i]-temp_speeds[len-i-1]);
			}
			alignments.push(Math.abs(d3.sum(diffs)));
		}
		this.wind_offset = this.pol_bearings[alignments.indexOf(d3.min(alignments))];
		console.log("Wind offset", this.wind_offset);

		this.r = d3.scale.linear()
			.domain([0, this.max_r*1.2])
			.range([0, radius]);

		this.mean_line = d3.svg.line.radial()
			.radius(function(d) { return that.r(d.mean); })
			.interpolate("cardinal-closed")
			.angle(function(d) { return Math.PI/180 * (-d.bearing); });

		this.max_line = d3.svg.line.radial()
			.radius(function(d) { return that.r(d.max); })
			.interpolate("cardinal-closed")
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

		this.polar_g = this.plot.append("g")
			.on("click", function() {
				console.log('got click');
				that.toggle_mode();
			});

		// The mean line
		this.polar_g.append("path")
			.datum(polars)
			.attr("class", "polar mean")
			.attr("d", this.mean_line);

		// The mean line
		this.polar_g.append("path")
			.datum(polars)
			.attr("class", "polar max")
			.attr("d", this.max_line);

		// The current bearing line
		this.marker = this.polar_g.append('svg:line')
			.attr('x2', this.r(this.speeds[this.marker_pos]))
			.attr("class", "polar bearing")
			.attr("transform", "rotate(" + (-(this.bearings[this.marker_pos]+90)) + ")");

		// The estimated wind direction
		this.wind = this.polar_g.append('svg:line')
			.attr('x2', this.r(d3.max(this.pol_speeds)))
			.attr("class", "polar wind")
			.attr("transform", "rotate(" + (-this.wind_offset+90) + ")");

	},

	movemarker: function(i) {
		this.marker_pos = (i < 0) ? 0 : (i >= this.speeds.length) ? this.speeds.length - 1 : i;
		this.marker
			.attr('x2', this.r(this.speeds[this.marker_pos]))
			.attr("transform", "rotate(" + (-(this.bearings[this.marker_pos]+90)) + ")");
	},

	toggle_mode: function(mode) {
		if (this.mode === 'actual') {
			// Switch label to relative to wind
			var data = d3.range(0, 181, 30);
			for (var i = 5; i; i--) {
				data.push(data[i]);
			}
			d3.selectAll('.a.axis text')
					.data(data)
				.text(function(d) { return d + "°"; });
			this.polar_g.transition().attr("transform", "rotate(" + (+(this.wind_offset-180)) + ")");
			this.mode = 'polar';
		} else {
			// Switch labels to cardinals
			d3.selectAll('.a.axis text')
					.data(d3.range(0, 360, 30))
				.text(function(d) { return d + "°"; });
			this.polar_g.transition().attr("transform", "rotate(0)");
			this.mode = 'actual';
		}
	}
};
