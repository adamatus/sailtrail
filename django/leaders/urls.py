"""Routing for activity related pages"""
from django.urls import path

from .views import LeaderboardView

app_name = 'leaders'  # pylint: disable=invalid-name

urlpatterns = [
    path('', LeaderboardView.as_view(), name='leaderboards'),
]
