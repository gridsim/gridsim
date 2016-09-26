from gridsim.cyberphysical.element.pqcontroller import PQController, ParamType
from gridsim.cyberphysical.element.gridlab import GridLabCyberPhysicalSystem
from gridsim.cyberphysical.simulation import CyberPhysicalModule

from gridsim.simulation import Simulator
from gridsim.timemanager import RealTimeManager

from gridsim.unit import units

readparam = [ParamType.I1, ParamType.U1]
writeparam = [ParamType.P, ParamType.Q]

pqcontroller = PQController(readparam, writeparam)
grid = GridLabCyberPhysicalSystem("gridlabcyberphysicalsystem")

host = [] #define read address and write address on the physical devices

grid.initialize(readparam, writeparam, host)
grid.add(pqcontroller)

Simulator.register_simulation_module(CyberPhysicalModule)
sim = Simulator(RealTimeManager(1*units.seconds))

sim.cyberphysicalmodule.add(grid)

sim.reset()
print('start simulation')
sim.run(200 * units.seconds, 10 * units.seconds)
print('end simulation')