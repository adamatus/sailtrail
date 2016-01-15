"""Routing for healthcheck related pages"""
from django.conf.urls import url

from healthcheck.views import HealthcheckView

urlpatterns = [
    url(r'^$', HealthcheckView.as_view(), name='healthcheck'),
]
