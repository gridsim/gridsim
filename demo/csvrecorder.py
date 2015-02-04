from gridsim.unit import units

from gridsim.simulation import Simulator
from gridsim.recorder import PlotRecorder
from gridsim.thermal.core import ThermalProcess, ThermalCoupling
from gridsim.iodata.output import CSVSaver

# Create a simulation.
sim = Simulator()

# Setup topology (For simplicity we just take a trivial thermal simulation):
#           __________                             ___________
#          |          |       ___________         |           |
#          | hot_room |]-----| coupling  |-------[| cold_room |
#          |          |      |    1m2    |        |           |
#          |   60 C   |      |__100_W/K__|        |    20 C   |
#          |__________|      <----------->        |___________|
#                                 1m
#
celsius = units(60, units.degC)
hot_room = sim.thermal.add(ThermalProcess.room('hot_room',
                                               50*units.meter*units.meter,
                                               2.5*units.metre,
                                               celsius.to(units.kelvin)))

celsius = units(20, units.degC)
cold_room = sim.thermal.add(ThermalProcess.room('cold_room',
                                                50*units.meter*units.meter,
                                                2.5*units.metre,
                                                celsius.to(units.kelvin)))

sim.thermal.add(ThermalCoupling('coupling',
                                100*units.thermal_conductivity,
                                hot_room, cold_room))

# Add the temperature recorder.
temperature_recorder = PlotRecorder('temperature', units.second, units.degC)
sim.record(temperature_recorder,
           sim.thermal.find(instance_of=ThermalProcess))

# Add the power recorder.
power_recorder = PlotRecorder('power', units.second, units.watt)
sim.record(power_recorder, sim.thermal.find(instance_of=ThermalCoupling))

# Simulate
sim.run(1*units.hours, 10*units.minutes)

CSVSaver(temperature_recorder).save("./output/temp.csv")
