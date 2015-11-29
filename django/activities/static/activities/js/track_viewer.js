'use strict';

var L = require('leaflet'),
    d3 = require('d3');

module.exports = {
    latlng: [],
    map: null,
    marker: null,
    marker_pos: 0,
    // tile_source: 'http://{s}.tile.osm.org/{z}/{x}/{y}.png',
    // attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
    // subdomains: 'abc',

    // tile_source: 'http://{s}.tile.stamen.com/watercolor/{z}/{x}/{y}.jpg',
    // attribution: ['Map tiles by <a href="http://stamen.com/">Stamen Design</a>, ',
    //               'under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. ',
    //               'Data by <a href="http://openstreetmap.org/">OpenStreetMap</a>, ',
    //               'under <a href="http://creativecommons.org/licenses/by-sa/3.0">CC BY SA</a>.',
    //               ].join(''),
    // subdomains: 'abc',

    // tile_source: 'http://otile{s}.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.jpg',
    // tile_source: '//otile{s}-s.mqcdn.com/tiles/1.0.0/sat/{z}/{x}/{y}.jpg',
    tile_source: '',
    attribution: 'Tiles by <a href="http://www.mapquest.com/">MapQuest</a> &mdash; Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
    subdomains: '1234',


    /**
     * Main function to initialize leaflet map with track
     *
     * @param {Object} data Arrays of track info
     * @param {Number} max_speed Precomputed max speed, used for axis max
     */
    draw_map: function(data, max_speed, time_slider) {
        var i, len, color_scale, trkpnt,
            self = this;

        this.max_speed = max_speed;

        this.latlng = [];
        for (i = 0; i < data.lat.length; i++) {
            trkpnt = new L.latLng(data.lat[i], data.lon[i]);

            trkpnt.speed = data.speed[i];
            this.latlng.push(trkpnt);
        }

        this.map = L.map('map', {scrollWheelZoom: false});
        L.tileLayer(this.tile_source, {
            attribution: this.attribution,
            subdomains: this.subdomains,
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
            time_slider.on('slide', function movepolarmaker(slideEvnt, d) {
                var newdata = d | slideEvnt.value;

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


