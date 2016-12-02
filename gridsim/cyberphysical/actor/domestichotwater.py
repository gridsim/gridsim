"""
.. moduleauthor:: Michael Clausen <clm@hevs.ch>

.. codeauthor:: Michael Clausen <clm@hevs.ch>
.. codeauthor:: Gillian Basso <gillian.basso@hevs.ch>
.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

import types
import math

from gridsim.decorators import accepts, returns
from gridsim.util import Material, Water

from gridsim.unit import units

from gridsim.timeseries import TimeSeries

from gridsim.cyberphysical.element import Actor
from gridsim.cyberphysical.simulation import CyberPhysicalModuleListener

from gridsim.electrical.core import AbstractElectricalCPSElement


class BoilerMaterial(Material):
    def __init__(self):
        """
        Implementation of steel:

        * Thermal capacity: ``unknown (None)``
        * Weight: ``unknown (None)``
        * Thermal conductivity ``0.04 W/Km``

        """
        super(BoilerMaterial, self).__init__(None, None, 0.04)


class Boiler(AbstractElectricalCPSElement, Actor, CyberPhysicalModuleListener):
    @accepts((1, str),
             (9, TimeSeries),
             (12, (types.FunctionType, types.NoneType)))
    @units.wraps(None, (None, None, units.metre, units.metre, units.metre, units.kelvin,
                        units.watt / (units.kelvin * (units.meter * units.meter)), units.watt, units.kelvin, None, None,
                        None))
    def __init__(self, friendly_name, height, radius, thickness,
                 initial_temperature, heat_transfer_coeff, power,
                 temperature_in,
                 time_series,
                 readparamlist, writeparamlist,
                 time_converter=None):
        """

        :param friendly_name: Friendly name to give to the process.
        :type friendly_name: str, unicode
        :param height: the height of the boiler
        :type height: units.metre
        :param radius: the radius of the boiler
        :type radius: units.metre
        :param thickness: the thickness of the boiler
        :type thickness: units.metre
        :param initial_temperature: the initial temperature of the water
                                    in the boiler.
        :type initial_temperature: units.kelvin
        :param heat_transfer_coeff: the heat transfer coefficient
        :type heat_transfer_coeff: units.watt/(units.kelvin*(units.meter**2)
        :param power: the electrical power to heat the boiler
        :type power: units.watt
        :param temperature_in: the temperature of the input water
        :type temperature_in: units.kelvin
        :param time_series: the time_series to load the stream
        :type time_series: class:`gridsim.timeseries.TimeSeries`
        :param readparamlist: read parameter of the actor
        :param writeparamlist: write parameter of the actor
        :param time_converter:
        :type time_converter: types.FunctionType or ``None``
        :return:
        """

        # HACK: when object is constructed with *args or **kwargs
        if not isinstance(height, (int, float)):
            height = units.value(units.to_si(height))
        if not isinstance(radius, (int, float)):
            radius = units.value(units.to_si(radius))
        if not isinstance(thickness, (int, float)):
            thickness = units.value(units.to_si(thickness))
        if not isinstance(initial_temperature, (int, float)):
            initial_temperature = units.value(units.to_si(initial_temperature))
        if not isinstance(heat_transfer_coeff, (int, float)):
            heat_transfer_coeff = units.value(units.to_si(heat_transfer_coeff))
        if not isinstance(temperature_in, (int, float)):
            temperature_in = units.value(units.to_si(temperature_in))
        if not isinstance(power, (int, float)):
            power = units.value(units.to_si(power))

        super(Boiler, self). \
            __init__(friendly_name)

        self.readparamtype = readparamlist
        self.writeparamtype = writeparamlist

        self._time_converter = time_converter

        self._time_series = time_series
        self._time_series.load(time_converter=time_converter)

        self._height = height
        self._radius = radius
        self._thickness = thickness

        self._initial_temperature = initial_temperature
        self._temperature = self._initial_temperature

        self._heat_transfer_coeff = heat_transfer_coeff

        self._power = power
        self.old_power = 0

        self._temperature_in = temperature_in

        # potential energy [J/K]
        self._cb = units.value(Water().thermal_capacity) * \
                   units.value(Water().weight) * math.pi * self._height * (self._radius ** 2)

        # global loss factor [W/K.m2]
        self._ub = 1 / ((1 / self._heat_transfer_coeff) +
                        (self._thickness / units.value(BoilerMaterial().thermal_conductivity)))

        # thermal losses when off [W/K]
        self._off_losses = self._ub * ((2. * math.pi * (self._radius ** 2)) +
                                       (2 * math.pi * self._height * self._radius))

        self._on = False

    @property
    def temperature(self):
        """
        The water temperature is consider as uniform in the tank.
        """
        return self._temperature

    @temperature.setter
    def temperature(self, t):
        self._temperature = t

    @property
    def on(self):
        """
        The ``on`` parameter allows to turn on or off the boiler.
        If ``on is True`` the boiler is running (maintains the boiler temperature between hysteresis), otherwise the
        boiler is shutdown (and cannot heat the water).
        """
        return self._on

    @on.setter
    def on(self, on_off):
        self._on = on_off

    @property
    def power(self):
        """
        The electrical power of the boiler ``power`` if heating, otherwise ``0``.
        """
        if self.on:
            return self._power
        else:
            return 0

    def reset(self):
        """
        reset(self)

        Sets the time to default (``0``).

        .. seealso:: :func:`gridsim.timeseries.TimeSeriesObject.set_time`
        """
        self._temperature = self._initial_temperature
        self._time_series.set_time()

    @accepts(((1, 2), (int, float)))
    def calculate(self, time, delta_time):
        self._time_series.set_time(time)
        unit_delta_time = delta_time

        if self._time_converter == None:
            volume = units.to_si(units(self._time_series.volume, units.litre)) * delta_time
        else:
            volume = units.to_si(units(self._time_series.volume, units.litre)) * delta_time / units.value(
                self._time_converter(1), units.second)

        # thermal losses when used [W/K]
        on_losses = units.value(volume) * units.value(Water().weight) * units.value(
            Water().thermal_capacity) / unit_delta_time

        # total thermal losses [W/K]
        losses = self._off_losses + on_losses

        self._temperature = self._temperature + \
                            ((unit_delta_time * losses / self._cb) * (self._temperature_in - self._temperature)) + \
                            (unit_delta_time / self._cb) * self.power

    @accepts((2, (int, float)))
    def notify_read_param(self, info, data):
        pass

    @returns((int, float))
    def get_value(self, info):
        # return the consumption of the boiler when it's on
        if info in self.writeparamtype:
            if self._on:
                return self._power
                # no consumption when the boiler is off
            else:
                return 0

    def cyberphysical_module_end(self):
        print 'end simulation from Boiler'
