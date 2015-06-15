'use strict';

var track_viewer = require('./track_viewer');

describe('track_viewer', function() {

    var pos = {
            lat: [45, 46],
            lon: [-90, -91],
            time: ['2013-02-05T20:01:13+0000', '2013-02-05T20:01:14+0000'],
            speed: [10, 11],
        },
        element;

    beforeEach(function() {
        // Create a map element so we can attach map to it
        element = document.createElement('div');
        element.id = 'map';
        document.body.appendChild(element);

        // Don't download map tiles
        track_viewer.tile_source = '';
    });

    afterEach(function() {
        element.parentNode.removeChild(element);
    });

    describe('draw_map', function() {

        it('should respond', function() {
            track_viewer.should.respondTo('draw_map');
        });

        it('should populate latlng', function() {
            track_viewer.latlng.should.have.length(0);
            track_viewer.draw_map(pos);
            track_viewer.latlng.should.have.length(2);
        });
    });

    describe('move_marker', function() {
        beforeEach(function() {
            track_viewer.draw_map(pos);
        });

        afterEach(function() {
            // Remove map
            var el = document.getElementById('map');

            while (el.firstChild) {
                el.removeChild(el.firstChild);
            }
        });

        it('should move marker with valid position', function() {
            track_viewer.move_marker(1);
            track_viewer.marker_pos.should.equal(1);
        });

        it('should move marker to start with less than 0 position', function() {
            track_viewer.move_marker(-10);
            track_viewer.marker_pos.should.equal(0);
        });

        it('should move marker to end with greater than length position', function() {
            track_viewer.move_marker(10);
            track_viewer.marker_pos.should.equal(1);
        });
    });
});
