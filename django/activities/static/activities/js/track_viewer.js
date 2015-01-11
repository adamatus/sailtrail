var L = require("leaflet"),
		d3 = require("d3");
require("Leaflet.MultiOptionsPolyline");

module.exports = {
	latlng: [],
	map: null,
	trackline: null,
	marker: null,
	marker_pos: 0,
	//tile_source: 'http://{s}.tile.osm.org/{z}/{x}/{y}.png',
	tile_source: '',

	drawmap: function(pos) {

		this.max_speed = d3.max(pos.map(function(d) { return d.speed; }));
		console.log(this.max_speed);

		this.latlng = [];
		for(var i=0; i<pos.length; i++) { 
			var trkpnt = new L.latLng(pos[i].lat, pos[i].lon);
			trkpnt.speed = pos[i].speed;
			this.latlng.push(trkpnt);
		}

		this.map = L.map('map', {scrollWheelZoom: false});
		L.tileLayer(this.tile_source, {
			attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
			maxZoom: 18
		}).addTo(this.map);

		this.trackline = L.multiOptionsPolyline(this.latlng, {
			multiOptions: {
				fnContext: this,
				optionIdxFn: function(latLng) {
					// Percentage of max speed, rounded to fall into one of the color bins
					console.log((latLng.speed/this.max_speed));
					var out = Math.round((latLng.speed/this.max_speed)*5);

					return out;
				},
				options: [
					{color: "#1a9850"}, // 0
					{color: "#91cf60"}, // 20%
					{color: "#d9ef8b"}, // 40%
					{color: "#fee08b"}, // 60%
					{color: "#fc8d59"}, // 80%
					{color: "#d73027"}  // 100%
				]
			},
			opacity: 1,
			lineCap: 'butt',
			lineJoin: 'round',
			smoothFactor: 1
		}).addTo(this.map);
		this.marker = L.circleMarker(this.latlng[this.marker_pos], {
			radius: 6,
			color: 'red',
			weight: 3,
		}).addTo(this.map);
		this.map.fitBounds(this.trackline.getBounds());
	},

	movemarker: function(i) {
		this.marker_pos = (i < 0) ? 0 : (i >= this.latlng.length) ? this.latlng.length - 1 : i;
		this.marker.setLatLng(this.latlng[this.marker_pos]);
	}
};


