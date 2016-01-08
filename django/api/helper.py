"""Helper functions for accessing API data

Should this site ever be split into separate website and
API layers, this helper can be replaced with services calls
rather than direct model access"""
from typing import Dict, List

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet, Max, Q, Count, Sum
from django.http import HttpRequest

from api.models import Activity, ActivityTrack, ACTIVITY_CHOICES


def create_new_activity_for_user(user: User) -> Activity:
    """Helper to create a new Activity for a user"""
    return Activity.objects.create(user=user)


def get_activity_by_id(activity_id: int) -> Activity:
    """Helper to return an activity by Id"""
    return Activity.objects.get(id=activity_id)


def get_activities_for_user(cur_user: User) -> QuerySet:
    """Get activities, include current users private activities"""
    activities = Activity.objects.exclude(name__isnull=True)

    # Remove private activities for all but the current user
    return activities.exclude(
        ~Q(user__username=cur_user.username), private=True)


def get_users_activities(user: User, cur_user: User) -> QuerySet:
    """Get list of activities, including private activities if cur user"""
    activities = Activity.objects.filter(
        user__username=user.username)

    # Filter out private activities if the user is not viewing themselves
    if cur_user.username != user.username:
        activities = activities.filter(private=False)

    return activities


def get_public_activities() -> QuerySet:
    """Helper to return all public activities"""
    return Activity.objects.filter(private=False)


def verify_private_owner(activity: Activity, request: HttpRequest) -> None:
    """Helper to verify private ownership"""

    # Convert track to activity, if necessary
    if isinstance(activity, ActivityTrack):
        activity = activity.activity_id

    if activity.private and request.user != activity.user:
        raise PermissionDenied


def get_active_users() -> QuerySet:
    """Helper to return all public users"""
    return User.objects.filter(is_active=True, is_superuser=False)


def get_leaders() -> List[Dict[str, str]]:
    """Build list of leaders for the leaderboard"""
    leader_list = _get_activity_leaders()

    leaders = []

    for key, category in ACTIVITY_CHOICES:
        values = [x for x in leader_list if x['category'] == key]
        if len(values) > 0:
            leaders.append({'category': category, 'leaders': values})

    return leaders


def _get_activity_leaders() -> QuerySet:
    """Get the leaders for activities"""
    return Activity.objects.filter(private=False).values(
        'user__username', 'category').annotate(
            max_speed=Max('model_max_speed')).order_by('-max_speed')


def summarize_by_category(activities: QuerySet) -> QuerySet:
    """Summarize activities by category"""
    return activities.values('category').annotate(
        count=Count('category'),
        max_speed=Max('model_max_speed'),
        total_dist=Sum('model_distance')).order_by('-max_speed')
