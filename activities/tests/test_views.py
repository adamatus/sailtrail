from django.test import TestCase
from activities.models import Activity


class HomePageTest(TestCase):
    """Tests for Homepage"""

    def test_home_page_renders_home_template(self):
        """Make sure that the homepage is using the correct template"""
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_shows_existing_filenames(self):
        Activity.objects.create(filename='test1.sbn')
        Activity.objects.create(filename='test2.sbn')
        response = self.client.get('/')

        self.assertContains(response, 'test1.sbn')
        self.assertContains(response, 'test2.sbn')

    def test_home_page_does_not_show_full_filepaths(self):
        Activity.objects.create(filename='test2.sbn', filepath='/test')
        response = self.client.get('/')

        self.assertNotContains(response, '/test')


class FileUploadTest(TestCase):

    def test_saving_POST_request(self):
        """Make sure that the upload filename is saved"""
        self.client.post('/activities/upload',
                         data={'filename': 'testfile.sbn'})

        self.assertEqual(Activity.objects.count(), 1)
        new_activity = Activity.objects.first()
        self.assertEqual(new_activity.filename, 'testfile.sbn')

    def test_POST_request_redirects_to_homepage(self):
        """Make sure that we are redirected after POST"""
        response = self.client.post('/activities/upload',
                                    data={'filename': 'testfile.sbn'})
        self.assertRedirects(response, '/')

    def test_saving_POST_request_splits_filename_and_path(self):
        """Make sure that the upload filename is saved"""
        self.client.post('/activities/upload',
                         data={'filename': '/test/testfile.sbn'})

        self.assertEqual(Activity.objects.count(), 1)
        new_activity = Activity.objects.first()
        self.assertEqual(new_activity.filename, 'testfile.sbn')
        self.assertEqual(new_activity.filepath, '/test')


class ActivityViewTest(TestCase):

    def test_uses_activity_template(self):
        a = Activity.objects.create(filename='test2.sbn', filepath='/test')
        response = self.client.get('/activities/{id}/'.format(id=a.id))
        self.assertTemplateUsed(response, 'activity.html')

    def test_displays_only_details_for_that_session(self):
        a = Activity.objects.create(filename='test1.sbn', filepath='/test')
        Activity.objects.create(filename='test2.sbn', filepath='/tast')

        response = self.client.get('/activities/{id}/'.format(id=a.id))

        self.assertContains(response, 'test1.sbn')
        self.assertContains(response, '/test')
        self.assertNotContains(response, 'test2.sbn')
        self.assertNotContains(response, '/tast')


