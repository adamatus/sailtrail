import pytest

from django.test import TestCase
from django.urls import reverse

from api.tests.factories import ActivityFactory
from users.tests.factories import UserFactory


@pytest.mark.integration
class TestLeaderboardViewIntegration(TestCase):

    def setUp(self):
        self.user1 = UserFactory.create(username='test1')
        self.user2 = UserFactory.create(username='test2')

        self.activity = ActivityFactory.create(max_speed=10,
                                               user=self.user1)
        ActivityFactory.create(max_speed=5, user=self.user1)
        ActivityFactory.create(max_speed=7, user=self.user2)

    def test_leaderboard_renders_correct_template(self):
        response = self.client.get(reverse('leaders:leaderboards'))
        self.assertTemplateUsed(response, 'leaderboards.html')

    def test_leaderboard_contains_high_speeds(self):
        response = self.client.get(reverse('leaders:leaderboards'))
        leaders = response.context['leaders']
        assert 1 == len(leaders)
        sailing = leaders[0]
        assert 'Sailing' == sailing['category']
        assert 2 == len(sailing['leaders'])
        leader = sailing['leaders'][0]
        assert 'test1' == leader['user__username']
        assert 10.0 == leader['max_speed']
        second = sailing['leaders'][1]
        assert 'test2' == second['user__username']
        assert 7.0 == second['max_speed']

    def test_leaderboard_does_not_contain_private_high_speeds(self):
        self.activity.private = True
        self.activity.save()
        response = self.client.get(reverse('leaders:leaderboards'))
        leaders = response.context['leaders']
        assert 1 == len(leaders)
        sailing = leaders[0]
        assert 'Sailing' == sailing['category']
        assert 2 == len(sailing['leaders'])
        leader = sailing['leaders'][0]
        assert 'test2' == leader['user__username']
        assert 7.0 == leader['max_speed']
        second = sailing['leaders'][1]
        assert 'test1' == second['user__username']
        assert 5.0 == second['max_speed']
