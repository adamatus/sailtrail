var should = require('chai').should(),
		track_viewer = require('../track_viewer');

describe("track_viewer", function() {

	var pos = [{lat: 45, lon: -90}, {lat: 46, lon: -91}],
			element;

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

			track_viewer.latlng.should.have.length(0);
			track_viewer.tile_source = ''; // Don't download map tiles
			track_viewer.drawmap(pos);
			track_viewer.latlng.should.have.length(2);
		
		});
	});

	describe("movemarker", function() {
		beforeEach(function() {
			track_viewer.tile_source = ''; // Don't download map tiles
			track_viewer.drawmap(pos);
		});

		afterEach(function() {
			// Remove map
			var el = document.getElementById("map");
			while (el.firstChild) {
			    el.removeChild(el.firstChild);
			}
		});

		it("should move marker with valid position", function() {
			track_viewer.movemarker(1);
			track_viewer.marker_pos.should.equal(1);
		});

		it("should move marker to start with less than 0 position", function() {
			track_viewer.movemarker(-10);
			track_viewer.marker_pos.should.equal(0);
		});

		it("should move marker to end with greater than length position", function() {
			track_viewer.movemarker(10);
			track_viewer.marker_pos.should.equal(1);
		});
	});
});
