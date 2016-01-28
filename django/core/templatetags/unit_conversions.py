"""Template tag helpers for converting units"""
from django import template

from api.models import ACTIVITY_CHOICES
from core import UNIT_SETTING, UNITS

register = template.Library()


def distance(value=None):
    """Convert distance from meters to specific units"""
    try:
        return "{} {}".format(
            round((value * UNITS.m).to(UNIT_SETTING['dist']).magnitude, 2),
            UNIT_SETTING['dist'])
    except (ValueError, TypeError):
        return "error"


def speed(value=None):
    """Convert speed from meters/s to specific units"""
    try:
        orig_speed = (value * UNITS.m / UNITS.s)
        return "{} {}".format(
            round(orig_speed.to(UNIT_SETTING['speed']).magnitude, 2),
            UNIT_SETTING['speed'])
    except (ValueError, TypeError):
        return "error"


def category(value=None):
    """Get full category name from summarized key"""
    if value is None:
        return "error"
    for key, val in ACTIVITY_CHOICES:
        if key == value:
            return val
    return "Unknown"


register.filter('distance', distance)
register.filter('speed', speed)
register.filter('category', category)
