from django import template
from activities import UNITS, units
from activities.models import ACTIVITY_CHOICES

register = template.Library()


def distance(value):
    """Convert distance from meters to specific units"""
    if value is None:
        return "error"
    return "{} {}".format(
        round((value * units.m).to(UNITS['dist']).magnitude, 2),
        UNITS['dist'])


def speed(value):
    """Convert speed from meters/s to specific units"""
    if value is None:
        return "error"
    return "{} {}".format(
        round((value * units.m/units.s).to(UNITS['speed']).magnitude, 2),
        UNITS['speed'])


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
