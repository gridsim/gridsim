"""
TODO:
This module provides as independent unit management as possible
"""
from pint import UnitRegistry


class _Unit(object):

    def __init__(self):
        self._registry = UnitRegistry()
        self._registry.define('heat_capacity = J/(g*K)')
        self._registry.define('mass_density = g/(m*m*m)')
        self._registry.define('thermal_conductivity = W/(K*m)')

    def __call__(self, *args, **kwargs):
        return self._registry.Quantity(args[0], args[1])

    def __getattr__(self, item):
        return getattr(self._registry, item)

    def value(self, quantity):
        if isinstance(quantity, self._registry.Quantity):
            return quantity.magnitude
        else:
            return quantity

    def unit(self, quantity):
        if isinstance(quantity, self._registry.Quantity):
            return str(quantity.units)
        else:
            return ""

    def dimension(self, quantity):
        if isinstance(quantity, self._registry.Quantity):
            return quantity.dimensionality
        else:
            return ""

    def convert(self, v, u):
        if isinstance(v, (int, float)):
            return self._registry.Quantity(v, u)
        else:
            return v.to(u)

units = _Unit()
