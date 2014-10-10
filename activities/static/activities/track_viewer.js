var latlng = [];

for(var i=0; i<pos.length; i++) { 
	latlng.push(L.latLng(pos[i].lat, pos[i].lon));
}

var map = L.map('map');
L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png',
{
	attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
	maxZoom: 18}).addTo(map);

var trackline = L.polyline(latlng, {color: 'red'}).addTo(map);
map.fitBounds(trackline.getBounds());
