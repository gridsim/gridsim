"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.core import AbstractSimulationElement

from gridsim.cyberphysical.element import Actor
from gridsim.cyberphysical.simulation import CyberPhysicalModuleListener

from gridsim.decorators import accepts, returns
from gridsim.unit import units


class Battery(Actor, AbstractSimulationElement, CyberPhysicalModuleListener):
    @accepts((1, str))
    @units.wraps(None, (None, None, units.watt_hour, units.watt_hour, units.watt, None, None))
    def __init__(self, friendly_name, start_energy, max_energy, power, read_params, write_params):
        """
        __init__(self,friendly_name,start_energy,max_energy,power,read_params,write_params)

        This :class:`Actor` simulates the behavior of a battery. The charge and discharge is considered equal.
        The battery reach a max energy when the battery is full and the empty state when the battery is low.

        .. note :: On consumption, the power is considered positive.
                   On injection, the power is considered negative.

        :param friendly_name: friendly name for the :class:`gridsim.core.AbstractSimulationElement`
        :param start_energy: amount of energy to start with
        :param max_energy: max energy of the battery, the battery will stop storing
        :param power: power rate for the storage and discharge
        :param read_params: read parameter for the actor
        :param write_params: write parameter for the actor
        """
        # HACK: when object is constructed with *args or **kwargs
        if not isinstance(start_energy, (int, float)):
            start_energy = units.value(units.to_si(start_energy))
        if not isinstance(max_energy, (int, float)):
            max_energy = units.value(units.to_si(max_energy))
        if not isinstance(power, (int, float)):
            power = units.value(units.to_si(power))

        Actor.__init__(self)
        AbstractSimulationElement.__init__(self, friendly_name)
        CyberPhysicalModuleListener.__init__(self)

        self.read_params = read_params
        self.write_params = write_params

        self._store = True
        self._over_load = False
        self._empty = False
        if start_energy < max_energy:
            self._energy = start_energy
            self.energy = start_energy
        else:
            self._energy = max_energy
            self.energy = max_energy

        self._max_energy = max_energy
        self._power = power

        # the simulation runs with second, this is the conversion factor
        self._energy_seconds_to_hours = 3600.0

    def reset(self):
        self.energy = self._energy

    @accepts(((1, 2), (int, float)))
    def update(self, time, delta_time):
        self.energy = self._energy

    @accepts(((1, 2), (int, float)))
    def calculate(self, time, delta_time):
        # get the amount of energy save or feed
        e = delta_time * self._power / self._energy_seconds_to_hours
        if self._store:
            # add energy to the battery in storage mode
            self._energy += e
        else:
            # get energy from the battery in unload mode
            self._energy -= e

        self._over_load = False
        self._empty = False
        # upper limit of the battery
        if self._energy > self._max_energy:
            self._energy = self._max_energy
            self._over_load = True

        # down limit of the battery
        if self._energy < 0:
            self._energy = 0
            self._empty = True

    @accepts((2, (int, float)))
    def notify_read_param(self, read_param, data):
        pass

    @returns((int, float))
    def get_value(self, write_param):
        if write_param in self.write_params:
            # save energy
            if self._store:
                if not self._over_load:
                    # in storage mode the power feed in the battery
                    return self._power
                else:
                    self._store = False
                    # the battery is full, so it doesn't load anymore
                    return 0
            # give energy
            elif not self._store:
                if not self._empty:
                    # in injection mode the power is taken from the battery
                    return -self._power
                else:
                    self._store = True
                    # the batter is empty, so it doesn't inject anymore
                    return 0
        return 0

    def cyberphysical_module_end(self):
        print 'end simulation from Battery'
