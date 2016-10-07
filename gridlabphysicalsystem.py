from gridsim.cyberphysical.element.pqcontroller import PQController, ParamType
from gridsim.cyberphysical.element.gridlab import GridLabCyberPhysicalSystem
from gridsim.cyberphysical.simulation import CyberPhysicalModule

from gridsim.simulation import Simulator
from gridsim.execution import RealTimeExecutionManager

from gridsim.unit import units

#actor parameters

readparam = [ParamType.I1, ParamType.I2, ParamType.I3, ParamType.U1, ParamType.U2, ParamType.U3, ParamType.PA]
writeparam = [ParamType.P, ParamType.Q]

pqcontroller = PQController(readparam, writeparam)

#gridlabsystem parameters

grid = GridLabCyberPhysicalSystem("gridlabcyberphysicalsystem")

sicam = ['sicam','153.109.14.52',502]
acs800 = ['acs800','153.109.14.51',502]

host = [sicam,acs800]

readgridlab = [ParamType.U1,ParamType.U2,ParamType.U3,ParamType.UN,
               ParamType.I1,ParamType.I2,ParamType.I3,ParamType.IN,
               ParamType.UL12,ParamType.UL23,ParamType.UL31,
               ParamType.USUM,ParamType.ISUM,
               ParamType.PL1,ParamType.PL2,ParamType.PL3,ParamType.PA,
               ParamType.QL1, ParamType.QL2, ParamType.QL3, ParamType.QA,
               ParamType.SL1, ParamType.SL2, ParamType.SL3, ParamType.SA]
readregister = {'all': 40201, 'quantity': ParamType.getQuantity()}
writegridlab = [ParamType.P,ParamType.Q]
writeregister = {ParamType.P: 1066-1,ParamType.Q: 1063-1} #1-2 drive

grid.initialize(readgridlab, readregister, writegridlab, writeregister, host, 21) #sicam on 1-2 drive
grid.add(pqcontroller)

#simulation paramters

Simulator.register_simulation_module(CyberPhysicalModule)
sim = Simulator(RealTimeExecutionManager(10 * units.seconds))

sim.cyberphysicalmodule.add(grid)

sim.reset()
print('start simulation')
sim.run(200 * units.seconds, 10 * units.seconds)
print('end simulation')