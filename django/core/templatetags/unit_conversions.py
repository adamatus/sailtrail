from activities import UNIT_SETTING, UNITS
from api.models import ACTIVITY_CHOICES
from django import template

register = template.Library()


def distance(value):
    """Convert distance from meters to specific units"""
    if value is None:
        return "error"
    return "{} {}".format(
        round((value * UNITS.m).to(UNIT_SETTING['dist']).magnitude, 2),
        UNIT_SETTING['dist'])


def speed(value):
    """Convert speed from meters/s to specific units"""
    if value is None:
        return "error"
    return "{} {}".format(
        round((value * UNITS.m / UNITS.s).to(UNIT_SETTING['speed']).magnitude,
              2),
        UNIT_SETTING['speed'])


def category(value):
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
