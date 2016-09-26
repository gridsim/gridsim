from gridsim.cyberphysical.element.pqcontroller import PQController, ParamType
from gridsim.cyberphysical.element.gridlab import GridLabCyberPhysicalSystem
from gridsim.cyberphysical.simulation import CyberPhysicalModule

from gridsim.simulation import Simulator
from gridsim.timemanager import RealTimeManager

from gridsim.unit import units

readparam = [ParamType.I, ParamType.U]
writeparam = [ParamType.P, ParamType.Q]

pqcontroller = PQController(readparam, writeparam)
grid = GridLabCyberPhysicalSystem("gridlabcyberphysicalsystem")



grid.initialize(readparam, writeparam)
grid.add(pqcontroller)

Simulator.register_simulation_module(CyberPhysicalModule)
sim = Simulator(RealTimeManager(1*units.seconds))

sim.cyberphysicalmodule.add(grid)

sim.reset()
print('start simulation')
sim.run(200 * units.seconds, 10 * units.seconds)
print('end simulation')