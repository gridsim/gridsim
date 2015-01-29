from gridsim.simulation import Simulator
from gridsim.unit import units
from gridsim.recorder import Recorder
from gridsim.thermal.core import ThermalProcess, ThermalCoupling


#Custom recorder.
class ConsoleRecorder(Recorder):

    def __init__(self, attribute_name, x_unit, y_unit):
        super(ConsoleRecorder, self).__init__(attribute_name, x_unit, y_unit)

    def on_simulation_reset(self, subjects):
        print 'RESET, observing: ' + str(subjects)

    def on_simulation_step(self, time):
        # time is given in SI unit (i.e. second)
        print 'time = ' + str(units.convert(time*units.second, self._x_unit)) + ':'

    def on_observed_value(self, subject, time, value):
        # time and value are given in SI unit (i.e. second and kelvin)
        print '    ' + subject + '.' + self.attribute_name +\
              ' = ' + str(units.convert(value*units.kelvin, self._y_unit))

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

# Add a custom console recorder to the attribute "temperature" of the hot
# room thermal process.
sim.record(ConsoleRecorder("temperature", units.second, units.degC),
           sim.thermal.find(element_class=ThermalProcess))

# Simulate
sim.run(1*units.hour, 5*units.minute)
