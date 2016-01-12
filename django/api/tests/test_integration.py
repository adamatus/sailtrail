import pytest

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.test import TestCase

from api.models import Activity, ActivityTrack
from api.tests.factories import UserFactory, ActivityTrackpointFactory


@pytest.mark.integration
class TestDeleteActivityViewIntegration(TestCase):

    def setUp(self):
        self.user = UserFactory.create(username='test')
        self.client.login(username='test', password='password')
        Activity.objects.create(user=self.user)

    def test_delete_redirects_to_homepage(self):
        response = self.client.get(reverse('delete_activity',
                                           args=[1]))
        self.assertRedirects(response, reverse('home'))

    def test_delete_removes_item_from_db(self):
        self.client.get(reverse('delete_activity', args=[1]))
        with pytest.raises(ObjectDoesNotExist):
            Activity.objects.get(id=1)


@pytest.mark.integration
class TestUntrimTrack(TestCase):

    def setUp(self):
        self.user = UserFactory.create(username='test')
        activity = Activity.objects.create(user=self.user)

        self.track = ActivityTrack.objects.create(activity_id=activity)
        self.start = ActivityTrackpointFactory.create(track_id=self.track)
        self.next = ActivityTrackpointFactory.create(track_id=self.track)
        self.penultimate = ActivityTrackpointFactory.create(
            track_id=self.track)
        self.end = ActivityTrackpointFactory.create(track_id=self.track)
        self.track.trim_start = self.next.timepoint
        self.track.trim_end = self.penultimate.timepoint
        self.track.trimmed = True
        self.track.save()

    def test_get_with_non_owner_returns_404_and_track_not_untrimmed(self):
        UserFactory.create(username='otheruser')
        self.client.login(username='otheruser', password='password')
        response = self.client.get(reverse('untrim_track',
                                           args=[1, 1]))
        assert response.status_code == 403
        self.assertTemplateUsed('403.html')

        track = ActivityTrack.objects.get(id=self.track.id)
        assert track.trimmed is True
        assert track.trim_start == self.next.timepoint
        assert track.trim_end == self.penultimate.timepoint

    def test_get_with_owner_redirects_to_activity_and_resets_track_trim(self):
        self.client.login(username='test', password='password')
        response = self.client.get(reverse('untrim_track',
                                           args=[1, 1]))
        assert response.status_code == 302
        self.assertRedirects(response, reverse('view_activity', args=[1]))

        track = ActivityTrack.objects.get(id=self.track.id)
        assert track.trimmed is False
        assert track.trim_start == self.start.timepoint
        assert track.trim_end == self.end.timepoint

    def test_without_login_redirects_to_login_page(self):
        response = self.client.get(reverse('untrim_track',
                                           args=[1, 1]))
        assert response.status_code == 302
        new_url = "%s?next=%s" % (reverse('account_login'),
                                  reverse('untrim_track', args=[1, 1]))
        self.assertRedirects(response, new_url)
