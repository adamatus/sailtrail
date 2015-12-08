"""Routing for activity related pages"""
from django.conf.urls import url

from .views import LeaderboardView

urlpatterns = [
    url(r'^$', LeaderboardView.as_view(), name='leaderboards'),
]
