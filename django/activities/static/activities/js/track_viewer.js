module.exports = {
	L: require("leaflet"),
	latlng: [],
	map: null,
	trackline: null,
	marker: null,
	marker_pos: 0,
	tile_source: 'http://{s}.tile.osm.org/{z}/{x}/{y}.png',

	drawmap: function(pos) {
		this.latlng = [];
		for(var i=0; i<pos.length; i++) { 
			this.latlng.push(L.latLng(pos[i].lat, pos[i].lon));
		}

		this.map = this.L.map('map', {scrollWheelZoom: false});
		this.L.tileLayer(this.tile_source, {
			attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
			maxZoom: 18
		}).addTo(this.map);

		this.trackline = this.L.polyline(this.latlng, {color: 'red'}).addTo(this.map);
		this.marker = this.L.circleMarker(this.latlng[this.marker_pos], {
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


