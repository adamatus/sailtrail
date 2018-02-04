"""Routing for user related pages"""
from django.conf.urls import url

from .views import BoatView, BoatListView, NewBoatView

app_name = 'boats'  # pylint: disable=invalid-name

urlpatterns = [
    url(r'^$', BoatListView.as_view(), name='boat_list'),
    url(r'^(?P<pk>\d+)/$', BoatView.as_view(), name='boat'),
    url(r'^new$', NewBoatView.as_view(), name='new_boat'),
]
