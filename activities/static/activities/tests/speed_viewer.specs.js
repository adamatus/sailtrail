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
		var spds = [10, 20];
	  SpeedViewer.drawplot(spds);	
		expect(document.getElementById("speed-plot-svg")).not.toBeNull();
	
	});
});
