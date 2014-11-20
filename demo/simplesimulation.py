from gridsim.unit import units
from gridsim.simulation import Simulator

# Create the main simulator object.
sim = Simulator()

# Build topology using the different simulation modules...

# Reset the simulation.
sim.reset()

# Do a single step of 100ms.
sim.step(100*units.milliseconds)

# Run the simulation from the
sim.run(1*units.hours, 100*units.milliseconds)