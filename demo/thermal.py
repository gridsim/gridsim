from gridsim.unit import units
from gridsim.simulation import Simulator
from gridsim.recorder import PlotRecorder
from gridsim.thermal.core import ThermalProcess, ThermalCoupling
from gridsim.thermal.element import TimeSeriesThermalProcess
from gridsim.timeseries import SortedConstantStepTimeSeriesObject
from gridsim.iodata.input import CSVReader
from gridsim.iodata.output import FigureSaver, CSVSaver

# Gridsim simulator.
sim = Simulator()

# Create a simple thermal process: A room thermal coupling between the room and
# the outside temperature.
#    ___________
#   |           |
#   |   room    |
#   |    20 C   |            outside <= example time series (CSV) file
#   |           |]- 3 W/K
#   |___________|
#
celsius = units(20, units.degC)
room = sim.thermal.add(ThermalProcess.room('room',
                                           50*units.meter*units.meter,
                                           2.5*units.metre,
                                           units.convert(celsius, units.kelvin)))
outside = sim.thermal.add(
    TimeSeriesThermalProcess('outside', SortedConstantStepTimeSeriesObject(CSVReader()),
                             './data/example_time_series.csv',
                             lambda t: t*units.hours,
                             temperature_calculator=
                                lambda t: units.convert(units(t, units.degC), units.kelvin)))

sim.thermal.add(ThermalCoupling('room to outside', 1*units.thermal_conductivity,
                                room, outside))

# Create a plot recorder that records the temperatures of all thermal processes.
temp = PlotRecorder('temperature', units.second, units.degC)
sim.record(temp, sim.thermal.find(has_attribute='temperature'))

print("Running simulation...")

# Run the simulation for an hour with a resolution of 1 second.
sim.reset(31*4*units.day)
sim.run(31*units.day, 1*units.hours)

print("Saving data...")

# Create a PDF document, add the two figures of the plot recorder to the
# document and close the document.
FigureSaver(temp, "Temperature").save('./output/thermal-example.pdf')
FigureSaver(temp, "Temperature").save('./output/thermal-example.png')
CSVSaver(temp).save('./output/thermal-example.csv')