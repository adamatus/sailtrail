var speed_viewer = require('./speed_viewer');

describe("Speed viewer", function() {

	var pos = [{'speed': 4.47084233261339, 'time': '20:25:51'},
						 {'speed': 4.2570194384449245, 'time': '20:25:52'}],
			element;

	// Stick units into global... BAD!
	window.units = {'speed': 'knots', 'dist': 'nmi'}; 

	beforeEach(function() {
		// Create a #speed-plot div element so we can attach plot to it
		element = document.createElement("div");
		element.id = "speed-plot";
		document.body.appendChild(element);
	});

	afterEach(function() {
		// Remove the #speed-plot div element
		element.parentNode.removeChild(element);
	});

	describe("drawplot", function() {
		it("should respond", function() {
			speed_viewer.should.respondTo("drawplot");
		});
	
		it("should create an svg element", function() {
			speed_viewer.drawplot(pos);	
			var svg = document.getElementById("speed-plot-svg");
			should.exist(svg);
		});
	});

	describe("movemarker", function() {
		beforeEach(function() {
			speed_viewer.drawplot(pos);	
		});

		afterEach(function() {
			var el = document.getElementById("speed-plot-svg");
			el.parentNode.removeChild(el);
		});

		it("should move marker with valid position", function() {
			speed_viewer.movemarker(1);
			speed_viewer.marker_pos.should.equal(1);
		});

		it("should move marker to start with less than 0 position", function() {
			speed_viewer.movemarker(-10);
			speed_viewer.marker_pos.should.equal(0);
		});

		it("should move marker to end with greater than length position", function() {
			speed_viewer.movemarker(10);
			speed_viewer.marker_pos.should.equal(1);
		});
	});
});
