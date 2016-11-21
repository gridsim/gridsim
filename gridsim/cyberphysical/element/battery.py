"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.core import AbstractSimulationElement

from gridsim.cyberphysical.external import Actor
from gridsim.cyberphysical.simulation import CyberPhysicalModuleListener

class Battery(Actor,AbstractSimulationElement,CyberPhysicalModuleListener):
    def __init__(self, friendly_name, start_energy, maxenergy, power, readparamlist, writeparamlist):
        """

        __init__(self,friendly_name,start_energy,maxenergy,power,readparamist,writeparamlist)

        This class simulate the behavior of a battery. The amount of energy is provided at the beginning.
        The load and the unload rate is the same, that provide the same time to load and to unload the battery.
        The battery reach a max energy when the battery is full and the empty state when the battery is low.
        With the command store, this is possible to change between load and unload. When the store is true the battery
        is in load state otherwise the in unload mode.
        On consumption the battery get current, the power is positive.
        On injection the battery give current, the power is negative.

        :param friendly_name: friendly name for the abstractsimulationelement
        :param start_energy: amount of energy to start with
        :param maxenergy: max energy of the battery, the battery will stop storing
        :param power: power rate for the storage and discharge
        :param readparamlist: read parameter for the actor
        :param writeparamlist: write parameter for the actor
        """
        Actor.__init__(self)
        AbstractSimulationElement.__init__(self,friendly_name)
        CyberPhysicalModuleListener.__init__(self)

        self.readparamtype = readparamlist
        self.writeparamtype = writeparamlist

        self._store = True
        self._overload = False
        self._empty = False
        if start_energy < maxenergy:
            self._energy = start_energy
            self.energy = start_energy
        else:
            self._energy = maxenergy
            self.energy = maxenergy

        self._maxenergy = maxenergy
        self._power = power

        #the simulation runs with second, this is the conversion factor
        self._energy_seconds_to_hours = 3600.0

    def init(self):
        pass

    def reset(self):
        self.energy = self._energy

    def update(self, time, delta_time):
        self.energy = self._energy

    def calculate(self, time, delta_time):
        #get the amount of energy save or feed
        e = delta_time*self._power/self._energy_seconds_to_hours
        if self._store:
            self._energy += e
        else:
            self._energy -= e

        print self._energy

        self._overload = False
        self._empty = False

        #limit at the border of the battery
        if self._energy > self._maxenergy:
            self._energy = self._maxenergy
            self._overload = True

        if self._energy < 0:
            self._energy = 0
            self._empty = True

    def notifyReadParam(self, info, data):
        pass

    def getValue(self, info):
        print info, self.writeparamtype
        if info in self.writeparamtype:
            #save energy
            if self._store:
                if not self._overload:
                    print self._energy, self._power
                    return self._power
                else:
                    self._store = False
                    return 0
            #give energy
            elif not self._store:
                if not self._empty:
                    print self._energy, -self._power
                    return -self._power
                else:
                    self._store = True
                    return 0

    def cyberphysicalModuleEnd(self):

        print 'end simulation from Battery'