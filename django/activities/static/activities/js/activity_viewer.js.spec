'use strict';

var activity_viewer = require('./activity_viewer');

describe('Activity viewer', function() {

    var pos = {details: [{'lon': -89.3895205, 'speed': 6.045356371490281, 'lat': 43.0875531, 'time': '2014-07-15T22:37:54+00:00'}, {'lon': -89.3895605, 'speed': 6.356371490280778, 'lat': 43.0875522, 'time': '2014-07-15T22:37:55+00:00'}, {'lon': -89.3896015, 'speed': 6.531317494600432, 'lat': 43.0875506, 'time': '2014-07-15T22:37:56+00:00'}, {'lon': -89.3896433, 'speed': 6.647948164146868, 'lat': 43.0875511, 'time': '2014-07-15T22:37:57+00:00'}], polars: [{bearing: 2.5, max: 10, mean: 1}, {bearing: 180, max: 5, mean: 10}]};

    describe('init', function() {
        it('should respond', function() {
            activity_viewer.should.respondTo('init');
        });
    });

    describe('setup', function() {
        it('should call trackviewer_viewer.drawmap', sinon.test(function() {
            this.stub(activity_viewer.track_viewer, 'drawmap');
            activity_viewer.setup(null, pos);
            activity_viewer.track_viewer.drawmap.should.have.been.called;
        }));

        it('should call speed_viewer.drawplot', sinon.test(function() {
            this.stub(activity_viewer.track_viewer, 'drawmap');
            this.stub(activity_viewer.speed_viewer, 'drawplot');
            activity_viewer.setup(null, pos);
            activity_viewer.speed_viewer.drawplot.should.have.been.called;
        }));
    });

    describe('setup_slider', function() {
        it('should respond', function() {
            activity_viewer.should.respondTo('setup_slider');
        });
    });

    describe('setup_trim_events', function() {
        it('should respond', function() {
            activity_viewer.should.respondTo('setup_trim_events');
        });
    });
});
