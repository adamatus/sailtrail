import pytest
from rest_framework import status
from rest_framework.test import APILiveServerTestCase
from django.urls import reverse


@pytest.mark.functional
class ActivitiesTest(APILiveServerTestCase):

    def test_healthcheck_returns_200(self):
        url = reverse('healthcheck')

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'DB: OK' in str(response.content)
