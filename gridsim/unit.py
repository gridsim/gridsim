"""
TODO:
This module provides as independent unit management as possible
"""
from pint import UnitRegistry

from .decorators import accepts, returns

units = UnitRegistry()
units.define('heat_capacity = J/(g*K)')
units.define('mass_density = g/(m*m*m)')
units.define('thermal_conductivity = W/(K*m)')
units.define('metre = m')  # respect the BIMP


@accepts((0, units.Quantity))
@returns((int, float, complex))
def value(quantity):
    return quantity.magnitude


@accepts((0, units.Quantity))
@returns(str)
def unit(quantity):
    return str(quantity.units)


@accepts((0, units.Quantity))
@returns(list)
def dimension(quantity):
    return quantity.dimesionality


@accepts((0, units.Quantity), (1, units.Quantity))
@returns(units.Quantity)
def convert(v, u):
    return v.to(u)
