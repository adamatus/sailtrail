describe("Speed viewer", function() {
	it("expects to find a div with id speed-plot", function() {
		expect(document.getElementById("speed-plot")).not.toBeNull();
	});

	it("expects d3 to be defined", function() {
	  expect(d3).toBeDefined();
	});

	it("expects SpeedViewer to be defined", function() {
	  expect(SpeedViewer).toBeDefined();
	});

	it("expects drawplot to create an svg element [SMOKE for SpeedViewer]", function() {
		var pos = [{'speed': 4.47084233261339, 'time': '20:25:51'},
		           {'speed': 4.2570194384449245, 'time': '20:25:52'}];
		units = {'speed': 'knots', 'dist': 'nmi'}; // Stick units into global... BAD!
	  SpeedViewer.drawplot(pos);	
		expect(document.getElementById("speed-plot-svg")).not.toBeNull();
	
	});
});
