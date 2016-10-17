from gridsim.cyberphysical.element.pqcontroller import ParamType
from gridsim.cyberphysical.element.pqcontroller import PQController
from gridsim.cyberphysical.element.gridlab import GridLabCyberPhysicalSystem
from gridsim.cyberphysical.simulation import CyberPhysicalModule

from gridsim.simulation import Simulator
from gridsim.execution import RealTimeExecutionManager

from gridsim.unit import units

import argparse
import os

# -sh 153.109.14.52 -sp 502 -ah 153.109.14.51 -ap 502 -n 2 -et 10 -ts 4 -st 1

parser = argparse.ArgumentParser(description='Simulate the content of a file over the Gridlab District')
parser.add_argument('-o','--outfile', help='Output file for the logging values, (current,voltage,...)', required=False)

parser.add_argument('-sh','--sicamhost', help='Host of sicam on the district unit', required=True)
parser.add_argument('-ah','--acs800host', help='Host of acs800 on the district unit', required=True)
parser.add_argument('-sp','--sicamport', help='Port of sicam on the district unit', required=True)
parser.add_argument('-ap','--acs800port', help='Port of acs800 on the district unit', required=True)
parser.add_argument('-n','--number', help='Specify the district number', required=True)

parser.add_argument('-st','--steptime', help='Time to increment to the next step', required=True)
parser.add_argument('-ts','--totalstep', help='End simulation time', required=True)
parser.add_argument('-et','--executiontime', help='Real time to next step', required=True)

args = vars(parser.parse_args())
print os.getcwd()

if 'outfile' not in args.keys() or args['outfile'] == None:
    args['outfile'] = os.getcwd() + '\log.csv'

readparam = [ParamType.un1_QA]

writeparam = [ParamType.un1_P, ParamType.un1_Q,
                   ParamType.un2_P, ParamType.un2_Q,
                   ParamType.un3_P, ParamType.un3_Q]

pqcontroller = PQController(readparam, writeparam)

pqcontroller.initConsole()

sicam = ['sicam',args['sicamhost'],args['sicamport']]
acs800 = ['acs800',args['acs800host'],args['acs800port']]
host = [sicam,acs800]

GridLabCyberPhysicalSystem.initModbus(host)

gridunit1 = GridLabCyberPhysicalSystem("gridlabcyberphysicalsystemunit1")

readgridlabunit1 = [ParamType.un1_U1, ParamType.un1_U2, ParamType.un1_U3, ParamType.un1_UN,
               ParamType.un1_I1, ParamType.un1_I2, ParamType.un1_I3, ParamType.un1_IN,
               ParamType.un1_UL12, ParamType.un1_UL23, ParamType.un1_UL31,
               ParamType.un1_USUM, ParamType.un1_ISUM,
               ParamType.un1_PL1, ParamType.un1_PL2, ParamType.un1_PL3, ParamType.un1_PA,
               ParamType.un1_QL1, ParamType.un1_QL2, ParamType.un1_QL3, ParamType.un1_QA,
               ParamType.un1_SL1, ParamType.un1_SL2, ParamType.un1_SL3, ParamType.un1_SA]
readregisterunit1 = {'all': 40201, 'quantity': ParamType.getQuantity()}
writegridlabunit1 = [ParamType.un1_P, ParamType.un1_Q]
writeregisterunit1 = {ParamType.un1_P: 1066 - 1, ParamType.un1_Q: 1063 - 1} #1-2 drive

gridunit1.initialize(readgridlabunit1, readregisterunit1, writegridlabunit1, writeregisterunit1, int(args['number'] + '1')) #sicam on 2 drive
gridunit1.add(pqcontroller)

gridunit2 = GridLabCyberPhysicalSystem("gridlabcyberphysicalsystemunit2")

readgridlabunit2 = [ParamType.un2_U1, ParamType.un2_U2, ParamType.un2_U3, ParamType.un2_UN,
               ParamType.un2_I1, ParamType.un2_I2, ParamType.un2_I3, ParamType.un2_IN,
               ParamType.un2_UL12, ParamType.un2_UL23, ParamType.un2_UL31,
               ParamType.un2_USUM, ParamType.un2_ISUM,
               ParamType.un2_PL1, ParamType.un2_PL2, ParamType.un2_PL3, ParamType.un2_PA,
               ParamType.un2_QL1, ParamType.un2_QL2, ParamType.un2_QL3, ParamType.un2_QA,
               ParamType.un2_SL1, ParamType.un2_SL2, ParamType.un2_SL3, ParamType.un2_SA]
readregisterunit2 = {'all': 40201, 'quantity': ParamType.getQuantity()}
writegridlabunit2 = [ParamType.un2_P, ParamType.un2_Q]
writeregisterunit2 = {ParamType.un2_P: 1084 - 1, ParamType.un2_Q: 1081 - 1} #3-4 drive

gridunit2.initialize(readgridlabunit2, readregisterunit2, writegridlabunit2, writeregisterunit2, int(args['number'] + '2')) #sicam on 4 drive
gridunit2.add(pqcontroller)

gridunit3 = GridLabCyberPhysicalSystem("gridlabcyberphysicalsystemunit3")

readgridlabunit3 = [ParamType.un3_U1, ParamType.un3_U2, ParamType.un3_U3, ParamType.un3_UN,
               ParamType.un3_I1, ParamType.un3_I2, ParamType.un3_I3, ParamType.un3_IN,
               ParamType.un3_UL12, ParamType.un3_UL23, ParamType.un3_UL31,
               ParamType.un3_USUM, ParamType.un3_ISUM,
               ParamType.un3_PL1, ParamType.un3_PL2, ParamType.un3_PL3, ParamType.un3_PA,
               ParamType.un3_QL1, ParamType.un3_QL2, ParamType.un3_QL3, ParamType.un3_QA,
               ParamType.un3_SL1, ParamType.un3_SL2, ParamType.un3_SL3, ParamType.un3_SA]
readregisterunit3 = {'all': 40201, 'quantity': ParamType.getQuantity()}
writegridlabunit3 = [ParamType.un3_P, ParamType.un3_Q]
writeregisterunit3 = {ParamType.un3_P: 1102 - 1, ParamType.un3_Q: 1099 - 1} #5-6 drive

gridunit3.initialize(readgridlabunit3, readregisterunit3, writegridlabunit3, writeregisterunit3, int(args['number'] + '3')) #sicam on 6 drive
gridunit3.add(pqcontroller)

Simulator.register_simulation_module(CyberPhysicalModule)

sim = Simulator(RealTimeExecutionManager(int(args['executiontime']) * units.seconds))

sim.cyberphysicalmodule.add(gridunit1)
#sim.cyberphysicalmodule.add(gridunit2)
#sim.cyberphysicalmodule.add(gridunit3)

sim.reset()
print('start simulation')
sim.run(int(args['totalstep']) * units.seconds, int(args['steptime']) * units.seconds)
print('end simulation')