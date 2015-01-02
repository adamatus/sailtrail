var should = require('chai').should(),
		speed_viewer = require('../speed_viewer');

describe("Speed viewer", function() {

	var element;

	beforeEach(function() {
		// Create a map element so we can attach map to it
		element = document.createElement("div");
		element.id = "speed-plot";
		document.body.appendChild(element);
	});

	afterEach(function() {
		element.parentNode.removeChild(element);
	});

	describe("drawplot", function() {
		var pos = [{'speed': 4.47084233261339, 'time': '20:25:51'},
							 {'speed': 4.2570194384449245, 'time': '20:25:52'}];

		window.units = {'speed': 'knots', 'dist': 'nmi'}; // Stick units into global... BAD!

		it("should respond", function() {
			speed_viewer.should.respondTo("drawplot");
		});
	
		it("should create an svg element", function() {
			speed_viewer.drawplot(pos);	
			var svg = document.getElementById("speed-plot-svg");
			should.exist(svg);
		});
	});
});
