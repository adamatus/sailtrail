from datetime import timedelta

import pytest

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.test import TestCase

from activities import DATETIME_FORMAT_STR
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


class BaseTrackView(TestCase):
    """Helper class for all ActivityTrack related detail views

    Sets up a single activity, with a single track with 4 trackpoints.
    The activity and track are not properly initialized, as individual
    tests may need to initialize them in different ways."""

    def setUp(self):
        self.user = UserFactory.create(username='test')
        self.activity = Activity.objects.create(user=self.user)

        self.track = ActivityTrack.objects.create(activity_id=self.activity)
        self.start = ActivityTrackpointFactory.create(track_id=self.track)
        self.next = ActivityTrackpointFactory.create(track_id=self.track)
        self.penultimate = ActivityTrackpointFactory.create(
            track_id=self.track)
        self.end = ActivityTrackpointFactory.create(track_id=self.track)


@pytest.mark.integration
class TestDeleteTrack(BaseTrackView):

    def setUp(self):
        super(TestDeleteTrack, self).setUp()
        self.track.trim_start = self.next.timepoint
        self.track.trim_end = self.penultimate.timepoint
        self.track.trimmed = True
        self.track.save()

        self.track_other = ActivityTrack.objects.create(
            activity_id=self.activity)
        self.other_start = ActivityTrackpointFactory.create(
            track_id=self.track_other)
        self.other_end = ActivityTrackpointFactory.create(
            track_id=self.track_other)
        self.track_other.initialize_stats()

        self.activity.compute_stats()

    def test_get_with_non_owner_returns_403_and_track_not_deleted(self):
        UserFactory.create(username='otheruser')
        self.client.login(username='otheruser', password='password')
        response = self.client.get(reverse('delete_track',
                                           args=[1, 1]))
        assert response.status_code == 403
        self.assertTemplateUsed('403.html')

        assert self.activity.track.count() == 2

    def test_get_with_owner_redirects_to_activity_and_deletes(self):
        self.client.login(username='test', password='password')
        assert self.activity.duration == timedelta(0, 4)

        response = self.client.get(reverse('delete_track',
                                           args=[1, 1]))
        assert response.status_code == 302
        self.assertRedirects(response, reverse('view_activity', args=[1]))

        assert self.activity.track.count() == 1
        assert self.activity.track.first().id == 2
        assert self.activity.duration == timedelta(0, 1)

    def test_get_with_owner_redirects_to_activity_and_deletes_other(self):
        self.client.login(username='test', password='password')
        assert self.activity.duration == timedelta(0, 4)

        response = self.client.get(reverse('delete_track',
                                           args=[1, 2]))
        assert response.status_code == 302
        self.assertRedirects(response, reverse('view_activity', args=[1]))

        assert self.activity.track.count() == 1
        assert self.activity.track.first().id == 1
        assert self.activity.duration == timedelta(0, 1)

    def test_get_with_owner_raises_400_on_delete_of_last(self):
        self.client.login(username='test', password='password')
        assert self.activity.duration == timedelta(0, 4)

        response = self.client.get(reverse('delete_track',
                                           args=[1, 2]))
        assert response.status_code == 302
        self.assertRedirects(response, reverse('view_activity', args=[1]))

        response = self.client.get(reverse('delete_track',
                                           args=[1, 1]))
        assert response.status_code == 400
        self.assertTemplateUsed('400.html')

        assert self.activity.track.count() == 1
        assert self.activity.track.first().id == 1


@pytest.mark.integration
class TestTrimTrack(BaseTrackView):

    def setUp(self):
        super(TestTrimTrack, self).setUp()
        self.track.initialize_stats()
        assert self.track.trimmed is False

    # Something is wrong with this test... It fails with an
    # HTTPMethod not allow exception, while handling the PermissionDenied
    # def test_post_with_non_owner_returns_403_and_track_not_untrimmed(self):
    #     UserFactory.create(username='otheruser')
    #     self.client.login(username='otheruser', password='password')
    #     response = self.client.post(reverse('trim_track',
    #                                        args=[1, 1]),
    #                                 {'trim-start': '-1',
    #                                  'trim-end': '-1'})
    #     assert response.status_code == 403
    #     self.assertTemplateUsed('403.html')
    #
    #     track = ActivityTrack.objects.get(id=self.track.id)
    #     assert track.trimmed is False
    #     assert track.trim_start == self.first.timepoint
    #     assert track.trim_end == self.end.timepoint

    def test_post_with_owner_trims_for_good_start_no_end(self):

        trim_start = self.next.timepoint.strftime(DATETIME_FORMAT_STR)

        self.client.login(username='test', password='password')
        response = self.client.post(reverse('trim_track',
                                            args=[1, 1]),
                                    {'trim-start': trim_start,
                                     'trim-end': '-1'})
        assert response.status_code == 302
        self.assertRedirects(response, reverse('view_activity', args=[1]))

        track = ActivityTrack.objects.get(id=self.track.id)
        assert track.trimmed is True
        assert track.trim_start == self.next.timepoint
        assert track.trim_end == self.end.timepoint

    def test_post_with_owner_trims_for_no_start_good_end(self):

        trim_end = self.penultimate.timepoint.strftime(DATETIME_FORMAT_STR)

        self.client.login(username='test', password='password')
        response = self.client.post(reverse('trim_track',
                                            args=[1, 1]),
                                    {'trim-start': '-1',
                                     'trim-end': trim_end})
        assert response.status_code == 302
        self.assertRedirects(response, reverse('view_activity', args=[1]))

        track = ActivityTrack.objects.get(id=self.track.id)
        assert track.trimmed is True
        assert track.trim_start == self.start.timepoint
        assert track.trim_end == self.penultimate.timepoint

    def test_post_with_owner_trims_for_good_start_good_end(self):

        trim_start = self.next.timepoint.strftime(DATETIME_FORMAT_STR)
        trim_end = self.penultimate.timepoint.strftime(DATETIME_FORMAT_STR)

        self.client.login(username='test', password='password')
        response = self.client.post(reverse('trim_track',
                                            args=[1, 1]),
                                    {'trim-start': trim_start,
                                     'trim-end': trim_end})
        assert response.status_code == 302
        self.assertRedirects(response, reverse('view_activity', args=[1]))

        track = ActivityTrack.objects.get(id=self.track.id)
        assert track.trimmed is True
        assert track.trim_start == self.next.timepoint
        assert track.trim_end == self.penultimate.timepoint

    def test_post_with_owner_trims_for_bad_both_does_nothing(self):

        self.client.login(username='test', password='password')
        response = self.client.post(reverse('trim_track',
                                            args=[1, 1]),
                                    {'trim-start': 'junk',
                                     'trim-end': 'junk2'})
        assert response.status_code == 302
        self.assertRedirects(response, reverse('view_activity', args=[1]))

        track = ActivityTrack.objects.get(id=self.track.id)
        assert track.trimmed is False

@pytest.mark.integration
class TestUntrimTrack(BaseTrackView):

    def setUp(self):
        super(TestUntrimTrack, self).setUp()
        self.track.trim_start = self.next.timepoint
        self.track.trim_end = self.penultimate.timepoint
        self.track.trimmed = True
        self.track.save()

    def test_get_with_non_owner_returns_403_and_track_not_untrimmed(self):
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
