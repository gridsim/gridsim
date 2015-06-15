from gridsim.unit import units
from gridsim.util import Position
from gridsim.simulation import Simulator
from gridsim.recorder import PlotRecorder
from gridsim.thermal.element import TimeSeriesThermalProcess
from gridsim.thermal.core import ThermalProcess, ThermalCoupling
from gridsim.electrical.core import AbstractElectricalCPSElement
from gridsim.electrical.network import ElectricalPQBus, \
    ElectricalTransmissionLine
from gridsim.electrical.loadflow import DirectLoadFlowCalculator
from gridsim.timeseries import SortedConstantStepTimeSeriesObject
from gridsim.iodata.input import CSVReader
from gridsim.iodata.output import FigureSaver

from gridsim.controller import AbstractControllerElement


class Thermostat(AbstractControllerElement):

    def __init__(self, friendly_name, target_temperature, hysteresis,
                 thermal_process, subject, attribute,
                 on_value=True, off_value=False, position=Position()):
        """
        A thermostat controller. This class measures the temperature of a
        thermal process (typically a room) and controls ANY attribute of any
        AbstractSimulationElement depending the measured temperature, the given
        target_temperature and the hysteresis.

        :param: friendly_name: User friendly name to give to the element.
        :type friendly_name: str

        :param: target_temperature: The temperature to try to maintain inside
            the target ThermalProcess.
        :type: target_temperature: temperature see :mod:`gridsim.unit`

        :param: hysteresis: The +- hysteresis in order to avoid to fast on/off
            switching.
        :type: hysteresis: delta temperature see :mod:`gridsim.unit`

        :param: thermal_process: The reference to the thermal process to
            observe.
        :type: thermal_process: :class:`.ThermalProcess`

        :param: subject: Reference to the object of which is attribute has to be
            changed depending on the temperature.
        :type: object

        :param: attribute: The name of the attribute to control as string.
        :type: str

        :param: on_value: The value to set for the attribute in order to turn
            the device "on".
        :type: on_value: any

        :param: off_on_value: The value to set for the attribute in order to
            turn the device "off".
        :type: off_value: any

        :param position: The position of the thermal element.
            Defaults to [0,0,0].
        :type position: :class:`Position`
        """
        super(Thermostat, self).__init__(friendly_name, position)
        self.target_temperature = units.value(target_temperature, units.kelvin)
        """
        The temperature to try to retain inside the observer thermal process by
        conducting an electrothermal element.
        """

        self.hysteresis = units.value(hysteresis, units.kelvin)
        """
        The +- hysteresis applied to the temperature measure in order to avoid
        to fast on/off switching.
        """

        if not hasattr(thermal_process, 'temperature'):
            raise TypeError('thermal_process')
        self.thermal_process = thermal_process
        """
        The reference to the thermal process to observe and read the
        temperature from.
        """

        self.subject = subject
        """
        The reference to the element to control.
        """

        self.attribute = attribute
        """
        Name of the attribute to control.
        """

        self.on_value = on_value
        """
        Value to set in order to turn the element on.
        """

        self.off_value = off_value
        """
        Value to set in order to turn the element off.
        """

        self._output_value = off_value

    # AbstractSimulationElement implementation.
    def reset(self):
        """
        AbstractSimulationElement implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationElement.reset`.
        """
        pass

    def calculate(self, time, delta_time):
        """
        AbstractSimulationElement implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationElement.calculate`.
        """
        actual_temperature = self.thermal_process.temperature

        if actual_temperature < (self.target_temperature - self.hysteresis / 2.):
            self._output_value = self.on_value
        elif actual_temperature > (self.target_temperature + self.hysteresis / 2.):
            self._output_value = self.off_value

    def update(self, time, delta_time):
        """
        AbstractSimulationElement implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationElement.update`.
        """
        setattr(self.subject, self.attribute, self._output_value)


class ElectroThermalHeaterCooler(AbstractElectricalCPSElement):
    def __init__(self, friendly_name, pwr, efficiency_factor, thermal_process):

        super(ElectroThermalHeaterCooler, self).__init__(friendly_name)

        self._efficiency_factor = units.value(efficiency_factor)

        self._thermal_process = thermal_process

        self.power = units.value(pwr, units.watt)

        self._on = False
        """
        Controls the heater/cooler. If this is True, the heater/cooler is active
        and takes energy from the electrical
        network to actually heat or cool the thermal process associated.
        """

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

# Gridsim simulator.
sim = Simulator()
sim.electrical.load_flow_calculator = DirectLoadFlowCalculator()

# Create a simple thermal process: A room and a thermal coupling between the
# room and the outside temperature.
#    ___________
#   |           |
#   |   room    |
#   |    20 C   |            outside <= example time series (CSV) file
#   |           |]- 3 W/K
#   |___________|
#
# The room has a surface of 50m2 and a height of 2.5m.
celsius = units(20, units.degC)
room = sim.thermal.add(ThermalProcess.room('room',
                                           50*units.meter*units.meter,
                                           2.5*units.metre,
                                           units.convert(celsius, units.kelvin)))

outside = sim.thermal.add(
    TimeSeriesThermalProcess('outside', SortedConstantStepTimeSeriesObject(CSVReader('./data/example_time_series.csv')),
                             lambda t: t*units.hour,
                             temperature_calculator=
                                lambda t: units.convert(units(t, units.degC),
                                                        units.kelvin)))
sim.thermal.add(ThermalCoupling('room to outside',
                                10.0*units.thermal_conductivity,
                                room, outside))

# Create a minimal electrical simulation network with a thermal heater connected
# to Bus0.
#
#                  Line0
#   SlackBus o----------------o Bus0
#                             |
#                heater (ElectricalHeaterCooler)
#
bus0 = sim.electrical.add(ElectricalPQBus('Bus0'))
sim.electrical.connect("Line0", sim.electrical.bus(0), bus0,
                       ElectricalTransmissionLine('Line0',
                                                  1000*units.metre,
                                                  0.2*units.ohm))

heater = sim.electrical.add(ElectroThermalHeaterCooler('heater',
                                                       1*units.kilowatt, 1.0,
                                                       room))
sim.electrical.attach(bus0, heater)

# Add the thermostat that controls the temperature inside the room and to hold
# it between 16..20 degrees celsius:
#                ____________
#               |            |       ____________
#               |    room    |      |            |
#               |        o----------| Thermostat |---\
#               |            |      |____________|   |
#               |  |^^^^^^|  |                       |
#               |__|heater|__|                       |
#                __|__    |__________________________|
#                 ---
#
target = units(20, units.degC)
# the hysteresis is a delta of temperature
hysteresis = 1*units.delta_degC

thermostat = sim.controller.add(Thermostat('thermostat',
                                           units.convert(target, units.kelvin),
                                           hysteresis,
                                           room, heater, 'on'))

# Create a plot recorder that records the temperatures of all thermal processes.
temp = PlotRecorder('temperature', units.second, units.degC)
sim.record(temp, sim.thermal.find(has_attribute='temperature'))

# Create a plot recorder that records the control value of the thermostat given
# to the heater.
control = PlotRecorder('on', units.second, bool)
sim.record(control, sim.electrical.find(has_attribute='on'))

# Create a plot recorder that records the power used by the electrical heater.
power = PlotRecorder('delta_energy', units.second, units.joule)
sim.record(power, sim.find(friendly_name='heater'))

print("Running simulation...")

# Run the simulation for an hour with a resolution of 1 second.
sim.reset()
sim.run(5 * units.hour, units.second)

print("Saving data...")

# Create a PDF document, add the two figures of the plot recorder to the
# document and close the document.
FigureSaver(temp, "Temperature").save('./output/thermostat-fig1.pdf')
FigureSaver(control, "Control").save('./output/thermostat-fig2.png')
FigureSaver(power, "Power").save('./output/thermostat-fig3.png')
