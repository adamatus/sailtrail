from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.test import TestCase

from api.models import Activity
from activities.tests.factories import UserFactory


class TestDeleteActivityView(TestCase):

    def setUp(self):
        self.user = UserFactory.create(username='test')
        self.client.login(username='test', password='password')
        Activity.objects.create(user=self.user)

    def test_delete_redirects_to_homepage(self):
        response = self.client.get(reverse('delete_activity',
                                           args=[1]))
        self.assertRedirects(response, '/')

    def test_delete_removes_item_from_db(self):
        self.client.get(reverse('delete_activity', args=[1]))
        self.assertRaises(ObjectDoesNotExist,
                          lambda: Activity.objects.get(id=1)
                          )
