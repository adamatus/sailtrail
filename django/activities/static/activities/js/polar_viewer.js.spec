'use strict';

var $ = require('jquery');

var polar_viewer = require('./polar_viewer');

describe('polar_viewer', function() {

    var pos = {
            speed: [10, 12, 12, 14],
            bearing: [1, 5, 8, 10],
    };

    beforeEach(function() {
        $('body').append('<div id="polar-plot"></div>');
        $('body').append('<input type="checkbox" id="polar-frame-of-ref"/>');
    });

    afterEach(function() {
        $('#polar-plot').remove();
        $('#polar-frame-of-ref').remove();
    });

    describe('draw_plot', function() {
        it('should respond', function() {
            polar_viewer.should.respondTo('draw_plot');
        });

        it('should create an svg element', function() {
            var svg;

            polar_viewer.draw_plot(pos);
            svg = document.getElementById('polar-plot-svg');
            should.exist(svg);
        });
    });

    describe('move_marker', function() {
        beforeEach(function() {
            polar_viewer.draw_plot(pos);
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
            polar_viewer.marker_pos.should.equal(3);
        });
    });

    describe('toggle_mode', function() {
        it('should respond', function() {
            polar_viewer.should.respondTo('toggle_mode');
        });

        beforeEach(function() {
            polar_viewer.draw_plot(pos);
        });

        it('should toggle the plot to boat-centered frame of reference', function() {
            $('#polar-frame-of-ref').prop('checked', true);
            polar_viewer.toggle_mode();
            $('#polar-plot-svg text').text().should.equal('510150°45°90°135°180°135°90°45°');
        });

        it('should toggle the plot to world-centered frame of reference', function() {
            $('#polar-frame-of-ref').prop('checked', false);
            polar_viewer.toggle_mode();
            $('#polar-plot-svg text').text().should.equal('51015NNEESESSWWNW');
        });
    });
});
