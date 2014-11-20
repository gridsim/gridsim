from gridsim.unit import units, convert
from gridsim.simulation import Simulator
from gridsim.thermal.core import ThermalCoupling, ThermalProcess
from gridsim.thermal.element import ConstantTemperatureProcess
from gridsim.recorder import PlotRecorder
from gridsim.iodata.output import FigureSaver, CSVSaver

# Gridsim simulator.
sim = Simulator()

# Create a simple thermal process: Two rooms and the thermal coupling between
# them and to the outside temperature.
#             __________                        ___________
#           |          |   ________________   |           |
#           |   room1  |]-| room1 to room2 |-[| cold_room |
#           |    18 C  |  |_____50_W/K_____|  |    25 C   |      outside 5 C
#  10 W/K -[|          |                      |           |]- 10 W/K
#           |__________|                      |___________|
#
celsius = units.Quantity(18, units.degC)
room1 = sim.thermal.add(ThermalProcess.room('room1',
                                            50*units.meter*units.meter,
                                            2.5*units.metre,
                                            celsius.to(units.kelvin)))
celsius = units.Quantity(25, units.degC)
room2 = sim.thermal.add(ThermalProcess.room('room2',
                                            50*units.meter*units.meter,
                                            2.5*units.metre,
                                            celsius.to(units.kelvin)))

celsius = units.Quantity(5, units.degC)
outside = sim.thermal.add(
    ConstantTemperatureProcess('outside', celsius.to(units.kelvin)))

sim.thermal.add(ThermalCoupling('room1 to outside',
                                10*units.thermal_conductivity,
                                room1, outside))
sim.thermal.add(ThermalCoupling('room2 to outside',
                                10*units.thermal_conductivity,
                                room2, outside))
sim.thermal.add(ThermalCoupling('room1 to room2',
                                50*units.thermal_conductivity,
                                room1, room2))

# Create a plot recorder that records the temperatures of all thermal processes.
kelvin = PlotRecorder('temperature')
sim.record(kelvin, sim.thermal.find(has_attribute='temperature'))

# Create a plot recorder that records the temperatures of all thermal
# processes in Kelvin.
celsius = PlotRecorder('temperature')
sim.record(celsius, sim.thermal.find(has_attribute='temperature'),
           lambda context: convert(context.value, units.degC))

# Create a second plot recorder which records all energy flows
# (thermal couplings) between the different processes.

flow = PlotRecorder('power')
sim.record(flow, sim.thermal.find(element_class=ThermalCoupling))

print("Running simulation...")

# Run the simulation for an hour with a resolution of 1 second.
sim.run(2*units.hour, 1*units.second)

print("Saving data...")

# Save the figures as images.
FigureSaver(kelvin, "Temperature (K)").save('./output/fig1.pdf')
FigureSaver(celsius, "Temperature (C)").save('./output/fig2.pdf')
FigureSaver(flow, "Flow").save('./output/fig3.pdf')

CSVSaver(celsius).save('./output/fig2.csv')