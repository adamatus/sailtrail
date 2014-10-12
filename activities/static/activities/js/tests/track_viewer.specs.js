describe("Track viewer", function() {
	it("expects to find a div with id map", function() {
		expect(document.getElementById("map")).not.toBeNull();
	});

	it("expects L to be defined", function() {
	  expect(L).toBeDefined();
	});

	it("expects TrackViewer to be defined", function() {
	  expect(TrackViewer).toBeDefined();
	});

	it("expects drawmap to populate latlng [SMOKE for TrackView.drawmap]", function(){
		var pos = [{lat: 45, lon: -90}, {lat: 46, lon: -91}];

		expect(TrackViewer.latlng.length).toEqual(0)
			TrackViewer.tile_source = ''; // Don't download map tiles
			TrackViewer.drawmap(pos);
		expect(TrackViewer.latlng.length).not.toEqual(0)
	
	});
});
