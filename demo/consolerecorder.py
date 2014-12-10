from gridsim.simulation import Simulator
from gridsim.unit import units
from gridsim.recorder import Recorder
from gridsim.thermal.core import ThermalProcess, ThermalCoupling
from gridsim.decorators import timed


#Custom recorder.
class ConsoleRecorder(Recorder):

    def __init__(self, attribute_name):
        super(ConsoleRecorder, self).__init__(attribute_name)

    @timed
    def on_simulation_reset(self, subjects):
        print 'RESET, observing: ' + str(subjects)

    @timed
    def on_simulation_step(self, time):
        print 'time = ' + str(time) + ':'

    def on_observed_value(self, subject, time, value):
        print '    ' + subject + '.' + self.attribute_name +\
              ' = ' + str(value)

# Create simulator.
sim = Simulator()

# Setup topology (For simplicity we just take a trivial thermal simulation):
#           __________                             ___________
#          |          |       ___________         |           |
#          | hot_room |]-----| coupling  |-------[| cold_room |
#          |   60 C   |      |   1m2     |        |           |
#          |          |      |__100_W/K__|        |    20 C   |
#          |__________|      <----------->        |___________|
#                                 1m

celsius = units.Quantity(60, units.degC)
hot_room = sim.thermal.add(ThermalProcess.room('hot_room',
                                               50*units.meter*units.meter,
                                               2.5*units.metre,
                                               celsius.to(units.kelvin)))

celsius = units.Quantity(20, units.degC)
cold_room = sim.thermal.add(ThermalProcess.room('cold_room',
                                                50*units.meter*units.meter,
                                                2.5*units.metre,
                                                celsius.to(units.kelvin)))

sim.thermal.add(ThermalCoupling('coupling',
                                100*units.thermal_conductivity,
                                hot_room, cold_room))

# Add a custom console recorder to the attribute "temperature" of the hot
# room thermal process.
sim.record(ConsoleRecorder("temperature"),
           sim.thermal.find(element_class=ThermalProcess))

# Simulate
sim.run(1*units.hour, 5*units.minute)
