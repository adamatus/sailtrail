from pint import UnitRegistry

units = UnitRegistry()
units.define('knots = knot')


UNITS = {'speed': 'knots',
         'dist': 'nmi'}

DATETIME_FORMAT_STR = "%Y-%m-%dT%H:%M:%S%z"
