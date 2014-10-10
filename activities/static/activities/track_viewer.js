var TrackViewer = {
	latlng: [],
	map: null,
	trackline: null,
	tile_source: 'http://{s}.tile.osm.org/{z}/{x}/{y}.png',

	drawmap: function(pos) {
		this.latlng = [];
		for(var i=0; i<pos.length; i++) { 
			this.latlng.push(L.latLng(pos[i].lat, pos[i].lon));
		}

		this.map = L.map('map');
		L.tileLayer(this.tile_source,
		{
			attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
			maxZoom: 18
		}).addTo(this.map);

		this.trackline = L.polyline(this.latlng, {color: 'red'}).addTo(this.map);
		this.map.fitBounds(this.trackline.getBounds());
	},
};


