"""Helper functions for accessing API data

Should this site ever be split into separate website and
API layers, this helper can be replaced with services calls
rather than direct model access"""
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpRequest

from api.models import Activity, ActivityTrack


def create_new_activity_for_user(user: User) -> Activity:
    """Helper to create a new Activity for a user"""
    return Activity.objects.create(user=user)


def get_activity_by_id(activity_id: int) -> Activity:
    """Helper to return an activity by Id"""
    return Activity.objects.get(id=activity_id)


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
