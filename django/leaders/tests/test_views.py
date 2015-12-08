from django.core.urlresolvers import reverse
from django.test import TestCase

from api.tests.factories import ActivityFactory
from users.tests.factories import UserFactory


class TestLeaderboardView(TestCase):

    def setUp(self):
        self.user1 = UserFactory.create(username='test1')
        self.user2 = UserFactory.create(username='test2')

        self.activity = ActivityFactory.create(model_max_speed=10,
                                               user=self.user1)
        ActivityFactory.create(model_max_speed=5, user=self.user1)
        ActivityFactory.create(model_max_speed=7, user=self.user2)

    def test_leaderboard_renders_correct_template(self):
        response = self.client.get(reverse('leaderboards'))
        self.assertTemplateUsed(response, 'leaderboards.html')

    def test_leaderboard_contains_high_speeds(self):
        response = self.client.get(reverse('leaderboards'))
        leaders = response.context['leaders']
        self.assertEqual(1, len(leaders), 'Should contain sailing entry')
        sailing = leaders[0]
        self.assertEqual('Sailing', sailing['category'])
        self.assertEqual(2, len(sailing['leaders']))
        leader = sailing['leaders'][0]
        self.assertEqual('test1', leader['user__username'])
        self.assertEqual(10.0, leader['max_speed'])
        second = sailing['leaders'][1]
        self.assertEqual('test2', second['user__username'])
        self.assertEqual(7.0, second['max_speed'])

    def test_leaderboard_does_not_contain_private_high_speeds(self):
        self.activity.private = True
        self.activity.save()
        response = self.client.get(reverse('leaderboards'))
        leaders = response.context['leaders']
        self.assertEqual(1, len(leaders), 'Should contain sailing entry')
        sailing = leaders[0]
        self.assertEqual('Sailing', sailing['category'])
        self.assertEqual(2, len(sailing['leaders']))
        leader = sailing['leaders'][0]
        self.assertEqual('test2', leader['user__username'])
        self.assertEqual(7.0, leader['max_speed'])
        second = sailing['leaders'][1]
        self.assertEqual('test1', second['user__username'])
        self.assertEqual(5.0, second['max_speed'])
