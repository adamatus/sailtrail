from pint import UnitRegistry

units = UnitRegistry()
units.define('knots = knot')


UNITS = {'speed': 'knots',
         'dist': 'nmi'}


