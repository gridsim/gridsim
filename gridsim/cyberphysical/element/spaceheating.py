"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.unit import units

from gridsim.cyberphysical.external import Actor
from gridsim.cyberphysical.simulation import CyberPhysicalModuleListener

from gridsim.electrical.core import AbstractElectricalCPSElement

class ElectroThermalHeaterCooler(AbstractElectricalCPSElement,Actor,CyberPhysicalModuleListener):
    def __init__(self, friendly_name, pwr, efficiency_factor, thermal_process, readparamlist, writeparamlist):
        """

        __init__(self, friendly_name, pwr, efficiency_factor, thermal_process, readparamlist, writeparamlist)

        This class simulate the behavior of a heat pump, this simulation can either heat of cool the air.
        This ElectroThermalHeaterCooler is based on the max power available for the heat or cool of the system.

        :param friendly_name: friendly name for the AbstractElectricalCPSElement
        :param pwr: power of the heatercooler system
        :param efficiency_factor: efficiency factor of the system
        :param thermal_process: thermal process of the system
        :param readparamlist: read parameter of the actor
        :param writeparamlist: write parameter of the actor
        """
        super(ElectroThermalHeaterCooler, self).__init__(friendly_name)

        self.readparamtype = readparamlist
        self.writeparamtype = writeparamlist

        self._efficiency_factor = units.value(efficiency_factor)

        self._thermal_process = thermal_process

        self.power = units.value(pwr, units.watt)

        self._on = False

    def init(self):
        pass

    @property
    def on(self):
        return self._on

    @on.setter
    def on(self, on_off):
        self._on = on_off

    # AbstractSimulationElement implementation.
    def reset(self):
        super(ElectroThermalHeaterCooler, self).reset()
        self.on = False

    def calculate(self, time, delta_time):
        self._internal_delta_energy = self.power * delta_time
        if not self.on:
            self._internal_delta_energy = 0

    def update(self, time, delta_time):
        super(ElectroThermalHeaterCooler, self).update(time, delta_time)
        self._thermal_process.add_energy(
            self._delta_energy * self._efficiency_factor)

    def notifyReadParam(self,info,data):
        pass

    def getValue(self,paramtype):
        #return the consumption of the heatercooler system on working state
        if paramtype in self.writeparamtype:
            if self._on:
                print 'on'
                return self.power
        #if the heater cooler system is not working return the consumption in stand-by mode
            else:
                print 'off'
                return 0

    def cyberphysicalReadBegin(self):
        pass

    def cyberphysicalModuleEnd(self):
        print 'end simulation from ElectroThermalHeaterCooler'