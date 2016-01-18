"""
GPX format handling.
"""
import gpxpy
import pytz
from django.core.files.uploadedfile import InMemoryUploadedFile


def create_trackpoints(track, uploaded_file: InMemoryUploadedFile, model):
    """Parse GPX trackpoints"""
    gpx = uploaded_file.read().decode('utf-8')
    gpx = gpxpy.parse(gpx)

    insert = []
    app = insert.append  # cache append method for speed.. maybe?

    prev_point = None
    speed = 0

    for gps_track in gpx.tracks:
        for segment in gps_track.segments:
            for point in segment.points:
                if prev_point is not None:
                    speed = point.speed_between(prev_point)
                prev_point = point
                app(model(
                    lat=point.latitude,
                    lon=point.longitude,
                    sog=speed,
                    timepoint=point.time.replace(tzinfo=pytz.UTC),
                    track=track))
    return insert
