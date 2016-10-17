from gridsim.util import Position
from gridsim.simulation import Simulator
from gridsim.electrical.core import AbstractElectricalCPSElement
from gridsim.electrical.network import ElectricalSlackBus
from gridsim.thermal.element import ThermalProcess

# Create the simulation.
sim = Simulator()

# Here you could create the topology of the actual simulation...
# ...

# Get all elements of the electrical simulation module
#   (Both statements do exactly the same).
print sim.find(module='electrical')
print sim.electrical.find()

# Get the electrical slack bus.
print sim.electrical.find(element_class=ElectricalSlackBus)

# Get all electrical consumer/producer/storage elements.
print sim.electrical.find(instance_of=AbstractElectricalCPSElement)

# Get the element with friendly name 'bus23'.
print sim.find(friendly_name='bus23')

# Get all elements which have the 'temperature' attribute.
print sim.find(has_attribute='temperature')

# Get all elements of the simulation that are close (1km)
#   to a given point (Route du rawyl 47, Sion).
print sim.find(close_to=(Position(46.240301, 7.358394, 566), 1000))

# Of course these search criteria can be mixed.
#   For example we search the 5th thermal process.
print sim.find(module='thermal', element_class=ThermalProcess, uid=5)
