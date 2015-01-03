var should = require('chai').should(),
		track_viewer = require('../track_viewer');

describe("track_viewer", function() {

	var element;

	beforeEach(function() {
		// Create a map element so we can attach map to it
		element = document.createElement("div");
		element.id = "map";
		document.body.appendChild(element);
	});

	afterEach(function() {
		element.parentNode.removeChild(element);
	});

	describe("drawmap", function() {

		it("should respond", function() {
			track_viewer.should.respondTo("drawmap");
		});

		it("should populate latlng", function(){
			var pos = [{lat: 45, lon: -90}, {lat: 46, lon: -91}];

			track_viewer.latlng.should.have.length(0);
			track_viewer.tile_source = ''; // Don't download map tiles
			track_viewer.drawmap(pos);
			track_viewer.latlng.should.have.length(2);
		
		});
	});
});
