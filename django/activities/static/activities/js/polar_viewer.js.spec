'use strict';

var polar_viewer = require('./polar_viewer');

describe('polar_viewer', function() {

    var polars = [
            {mean: 2.223, max: 5.691, bearing: 2.5},
            {mean: 2.522, max: 4.494, bearing: 7.5},
        ],
        pos = [
            {lat: 45, lon: -90},
            {lat: 46, lon: -91},
        ],
        element;

    beforeEach(function() {
        // Create a #polar-plot div element so we can attach plot to it
        element = document.createElement('div');
        element.id = 'polar-plot';
        document.body.appendChild(element);
    });

    afterEach(function() {
        // Remove the #polar-plot div element
        element.parentNode.removeChild(element);
    });

    describe('draw_plot', function() {
        it('should respond', function() {
            polar_viewer.should.respondTo('draw_plot');
        });

        it('should create an svg element', function() {
            var svg;

            polar_viewer.draw_plot(pos, polars);
            svg = document.getElementById('polar-plot-svg');
            should.exist(svg);
        });
    });

    describe('move_marker', function() {
        beforeEach(function() {
            polar_viewer.draw_plot(pos, polars);
        });

        afterEach(function() {
            var el = document.getElementById('polar-plot-svg');

            el.parentNode.removeChild(el);
        });

        it('should move marker with valid position', function() {
            polar_viewer.move_marker(1);
            polar_viewer.marker_pos.should.equal(1);
        });

        it('should move marker to start with less than 0 position', function() {
            polar_viewer.move_marker(-10);
            polar_viewer.marker_pos.should.equal(0);
        });

        it('should move marker to end with greater than length position', function() {
            polar_viewer.move_marker(10);
            polar_viewer.marker_pos.should.equal(1);
        });
    });

    describe('toggle_mode', function() {
        it('should respond', function() {
            polar_viewer.should.respondTo('toggle_mode');
        });

        beforeEach(function() {
            polar_viewer.draw_plot(pos, polars);
        });

        it('should toggle the mode from actual to polar', function() {
            polar_viewer.mode = 'actual';
            polar_viewer.toggle_mode();
            polar_viewer.mode.should.equal('polar');
        });

        it('should toggle the mode from polar to actual', function() {
            polar_viewer.mode = 'polar';
            polar_viewer.toggle_mode();
            polar_viewer.mode.should.equal('actual');
        });
    });
});
