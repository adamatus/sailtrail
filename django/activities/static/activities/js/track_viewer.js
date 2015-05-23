'use strict';

var L = require('leaflet'),
    d3 = require('d3');

module.exports = {
    latlng: [],
    map: null,
    marker: null,
    marker_pos: 0,
    tile_source: 'http://{s}.tile.osm.org/{z}/{x}/{y}.png',

    /**
     * Main function to initialize leaflet map with track
     *
     * @param {Array.<Object>} pos Array of timepoints with position info
     * @param {Number} max_speed Precomputed max speed, used for axis max
     */
    draw_map: function(pos, max_speed, time_slider) {
        var i, len, color_scale, trkpnt,
            self = this;

        this.max_speed = max_speed;

        this.latlng = [];
        for (i = 0; i < pos.length; i++) {
            trkpnt = new L.latLng(pos[i].lat, pos[i].lon);

            trkpnt.speed = pos[i].speed;
            this.latlng.push(trkpnt);
        }

        this.map = L.map('map', {scrollWheelZoom: false});
        L.tileLayer(this.tile_source, {
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 18,
        }).addTo(this.map);

        this.trackgroup = L.layerGroup().addTo(this.map);

        color_scale = d3.scale.linear()
            .domain([
                0,
                0.2 * this.max_speed,
                0.4 * this.max_speed,
                0.6 * this.max_speed,
                0.8 * this.max_speed,
                this.max_speed,
            ])
            .range(['#1a9850', '#91cf60', '#d9ef8b', '#fee08b', '#fc8d59', '#d73027']);

        for (i = 0, len = this.latlng.length; i < (len - 1); i++) {
            this.trackgroup.addLayer(L.polyline(this.latlng.slice(i, i + 2), {
                color: color_scale(this.latlng[i + 1].speed),
                lineCap: 'butt',
                lineJoin: 'round',
                opacity: 1,
            }));
        }

        this.marker = L.circleMarker(this.latlng[this.marker_pos], {
            radius: 6,
            color: 'red',
            weight: 3,
        }).addTo(this.map);

        this.map.fitBounds(this.latlng);

        // Register with slider to update positional marker
        if (time_slider) {
            time_slider.on('slide', function movepolarmaker(slideEvnt, data) {
                var newdata = data | slideEvnt.value;

                self.move_marker(newdata);
            });
        }
    },

    /**
     * Move the position marker to a new physical position on the track
     *
     * @param {Number} i The index in the speed array to move the marker to
     */
    move_marker: function(i) {
        this.marker_pos = (i < 0) ? 0 : (i >= this.latlng.length) ? this.latlng.length - 1 : i;
        this.marker.setLatLng(this.latlng[this.marker_pos]);
    },
};


