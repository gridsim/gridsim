from gridsim.simulation import Simulator
from gridsim.recorder import PlotRecorder
from gridsim.thermal.element import TimeSeriesThermalProcess
from gridsim.thermal.core import ThermalProcess, ThermalCoupling
from gridsim.electrical.network import ElectricalPQBus, ElectricalTransmissionLine

# Gridsim simulator.
sim = Simulator()

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
room = sim.thermal.add(ThermalProcess.room('room1', 50, 2.5, 20))
outside = sim.thermal.add(
    TimeSeriesThermalProcess('outside', './data/example_time_series.csv'))
sim.thermal.add(ThermalCoupling('room to outside', 10.0, room, outside))

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
                       ElectricalTransmissionLine('Line0', 1000, 0.2))
heater = sim.electrical.add(ElectroThermalHeaterCooler('heater', 1000,
                                                       1.0, room))
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
thermostat = sim.controller.add(Thermostat('thermostat', 18.0, 1.0, room,
                                           heater, 'on'))

# Create a plot recorder that records the temperatures of all thermal processes.
temp = PlotRecorder('Temperatures', PlotRecorder.HOUR, '{name}')
sim.record(temp, sim.thermal.find(has_attribute='temperature'),
           'temperature', 'C')

# Create a plot recorder that records the control value of the thermostat given
# to the heater.
control = PlotRecorder('Control', PlotRecorder.HOUR, '{name}')
sim.record(control, sim.electrical.find(has_attribute='on'), 'on')

# Create a plot recorder that records the power used by the electrical heater.
power = PlotRecorder('Power', PlotRecorder.HOUR, '{name}')
sim.record(power, sim.find(friendly_name='heater'), 'delta_energy', 'W',
           lambda context: context.value / context.delta_time)

# Run the simulation for an hour with a resolution of 1 second.
sim.reset()
sim.run(5 * Simulator.HOUR, Simulator.SECOND)

# Create a PDF document, add the two figures of the plot recorder to the
# document and close the document.
temp.save('./output/thermostat-fig1.png')
control.save('./output/thermostat-fig2.png')
power.save('./output/thermostat-fig3.png')
PlotRecorder.create_pdf('./output/thermostat-example.pdf').\
    add(temp).add(control).add(power).close()