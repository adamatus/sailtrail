from django.test import TestCase
from django.core.exceptions import ValidationError

from activities.models import Activity


class ActivityModelTest(TestCase):
    """Tests for the Activity model"""

    def test_can_save_simple_filename(self):
        activity = Activity(filename='test.sbn')
        activity.full_clean()  # Should not rase
        activity.save()

        self.assertIn(activity, Activity.objects.all())

    def test_cannot_save_empty_filename(self):
        activity = Activity()
        with self.assertRaises(ValidationError):
            activity.full_clean()  # Should rase

        self.assertNotIn(activity, Activity.objects.all())

    def test_can_save_full_filename(self):
        activity = Activity(filename='test.sbn', filepath='/test/')
        activity.full_clean()  # Should not rase
        activity.save()

        self.assertIn(activity, Activity.objects.all())
        saved_activity = Activity.objects.first()
        self.assertEqual(saved_activity.filepath, '/test/')
        self.assertEqual(saved_activity.filename, 'test.sbn')

