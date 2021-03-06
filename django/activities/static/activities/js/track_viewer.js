'use strict';

var L = require('leaflet'),
    d3 = require('d3'),
    $ = require('jquery');

module.exports = {
    latlng: [],
    map: null,
    marker: null,
    marker_pos: 0,
    trim_track: false,
    lower_marker: undefined,
    upper_marker: undefined,

    // One of "none", "osm", "stamen", "mapquest"
    source: 'none',

    map_tiles: {
        osm: {
            tile_source: 'http://{s}.tile.osm.org/{z}/{x}/{y}.png',
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
            subdomains: 'abc',
        },

        stamen: {
            tile_source: 'http://{s}.tile.stamen.com/watercolor/{z}/{x}/{y}.jpg',
            attribution: ['Map tiles by <a href="http://stamen.com/">Stamen Design</a>, ',
                'under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. ',
                'Data by <a href="http://openstreetmap.org/">OpenStreetMap</a>, ',
                'under <a href="http://creativecommons.org/licenses/by-sa/3.0">CC BY SA</a>.',
            ].join(''),
            subdomains: 'abc',
        },

        none: {
            tile_source: '',
            attribution: 'No map tiles loaded',
            subdomains: 'abc',
        },
    },

    /**
     * Main function to initialize leaflet map with track
     *
     * @param {Object} data Arrays of track info
     * @param {Number} max_speed Precomputed max speed, used for axis max
     * @param {Element} time_slider Time-slider element
     * @param {Element} trim_slider Trim-slider element
     * @param {Object} config Optional config details
     */
    draw_map: function(data, max_speed, time_slider, trim_slider, config) {
        var i,
            trkpnt,
            self = this;

        this.max_speed = max_speed;

        this.geo_json = [];
        this.latlng = [];
        for (i = 0; i < data.lat.length; i++) {
            trkpnt = new L.latLng(data.lat[i], data.lon[i]);

            trkpnt.speed = data.speed[i];
            this.latlng.push(trkpnt);

            // Create a temporary geo_json formatted array to use for leaflet
            // The activity JSON endpoint should be updated to return geoJSON
            if (i < (data.lat.length - 1)) {
                this.geo_json.push({
                    type: 'Feature',
                    properties: {
                        id: i,
                        speed: data.speed[i],
                    },
                    geometry: {
                        type: 'LineString',
                        coordinates: [
                            [data.lon[i], data.lat[i]],
                            [data.lon[i + 1], data.lat[i + 1]],
                        ],
                    },
                });
            }
        }

        if (this.source === 'mapquest') {
            this.map = L.map(
                'map', {
                    layers: MQ.mapLayer(),
                    scrollWheelZoom: false,
                }
            );
        } else {
            this.map = L.map(
                'map', {
                    scrollWheelZoom: false,
                }
            );
            L.tileLayer(this.map_tiles[this.source].tile_source, {
                attribution: this.map_tiles[this.source].attribution,
                subdomains: this.map_tiles[this.source].subdomains,
                maxZoom: 18,
            }).addTo(this.map);
        }

        this.map.fitBounds(this.latlng);

        this.color_scale = d3.scale.linear()
            .domain([
                0,
                0.2 * this.max_speed,
                0.4 * this.max_speed,
                0.6 * this.max_speed,
                0.8 * this.max_speed,
                this.max_speed,
            ])
            .range(['#1a9850', '#91cf60', '#d9ef8b', '#fee08b', '#fc8d59', '#d73027']);

        this.base_track = L.polyline(this.latlng, {
            color: 'grey',
            weight: 2,
            opacity: 0.5,
        });

        if (!trim_slider) {
            this.full_track = this.create_geo_json_layer(this.geo_json).addTo(this.map);
        }

        this.filtered_track = this.create_geo_json_layer(
            this.geo_json.filter(this.filter_recent_timepoints.bind(this)));

        this.marker = L.circleMarker(this.latlng[this.marker_pos], {
            radius: 6,
            color: 'red',
            weight: 3,
        });

        // Register with slider to update positional marker
        if (time_slider) {
            this.marker.addTo(this.map);
            time_slider.on('slide', function movepolarmaker(slideEvnt, d) {
                var newdata = d || slideEvnt.value;

                self.move_marker(newdata);
            });
        }

        if (trim_slider) {
            this.trim_track = true;
            this.base_track.addTo(this.map);

            if (config) {
                self.lower_marker = config.trim_start_index || self.lower_marker;
                self.upper_marker = config.trim_end_index || self.upper_marker;
            }

            this.full_track = L.polyline(this.latlng.filter(function(d, j) {
                return j >= self.lower_marker && j <= self.upper_marker;
            }), {
                smoothFactor: 0,
                color: 'black',
                weight: 3,
                opacity: 0.5,
            }).addTo(this.map);

            trim_slider.on('slide', function update_trim_slider_data(slideEvnt, d) {
                var newdata = d || slideEvnt.value;

                self.lower_marker = newdata[0];
                self.upper_marker = newdata[1];
                self.update_track();
            });
        }

        // Register with track-only-last-minute checkbox to optionally filter track
        this.filter_track = false;
        this.filter_state_changed = false;
        $('#track-only-last-minute').on('change', function(e) {
            self.filter_track = !!e.target.checked;
            self.filter_state_changed = true;
            self.update_track();
        });

    },

    /**
     * Filter recent timepoints, based on current marker position
     * @param data The individual timepoint to filter
     * @returns boolean
     */
    filter_recent_timepoints: function(data) {
        this.lower_marker = this.marker_pos - 60;
        this.upper_marker = this.marker_pos;
        return (data.properties.id <= this.upper_marker) && (data.properties.id > (this.lower_marker));
    },

    /**
     * Create a new geoJson leaflet layer, with speed-based coloring
     * @param geo_json The geoJSON to create the layer from
     */
    create_geo_json_layer: function(geo_json) {
        var self = this;

        return L.geoJson(geo_json, {
            style: function(pnt) {
                return {
                    color: self.color_scale(pnt.properties.speed),
                    lineCap: 'square',
                };
            },
        });
    },

    /**
     * Apply recency filtering, if necessary.
     */
    update_track: function() {
        var self = this;

        if (this.filter_track) {
            if (this.filter_state_changed) {
                // On initial change to filtered, remove full layer, add base
                this.map.removeLayer(this.full_track);
                this.map.addLayer(this.base_track);
                this.filter_state_changed = false;
            }

            // Remove old layers
            this.map.removeLayer(this.marker);
            this.map.removeLayer(this.filtered_track);

            // Create new filtered layer
            this.filtered_track = this.create_geo_json_layer(
                this.geo_json.filter(
                    this.filter_recent_timepoints.bind(this)));

            // Add filtered track and layers
            this.map.addLayer(this.filtered_track);
            this.map.addLayer(this.marker);
        } else if (this.trim_track) {
            this.full_track.setLatLngs(this.latlng.filter(function(d, i) {
                return i >= self.lower_marker && i <= self.upper_marker;
            }));
        } else if (this.filter_state_changed) {
            // Only reset back to unfiltered once, not on every call
            this.filter_state_changed = false;

            // Remove old layers
            this.map.removeLayer(this.base_track);
            this.map.removeLayer(this.filtered_track);
            this.map.removeLayer(this.marker);

            // Add full track and marker
            this.map.addLayer(this.full_track);
            this.map.addLayer(this.marker);
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
        this.update_track();
    },
};
