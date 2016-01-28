"""Core settings"""
from pint import UnitRegistry

UNITS = UnitRegistry()
UNITS.define('knots = knot')

UNIT_SETTING = {'speed': 'knots', 'dist': 'nmi'}

DATETIME_FORMAT_STR = "%Y-%m-%dT%H:%M:%S%z"
