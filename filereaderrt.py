"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.simulation import Simulator
from gridsim.cyberphysical.simulation import MinimalCyberPhysicalModule
from gridsim.execution import RealTimeExecutionManager

from gridsim.cyberphysical.simulation import CyberPhysicalModule
from gridsim.cyberphysical.element.gridlab import GridLabCyberPhysicalSystem

from gridsim.cyberphysical.element.pqfilereader import PQFileReader

from gridsim.cyberphysical.element.aggregator import SumAggregator
from gridsim.cyberphysical.element.converter import PConverter, QConverter

from paramtype import ParamType

from gridsim.unit import units

import argparse
import os

#Example of the file reader using the cyber-physical module with the following starting params
#-i pqfile.csv -sh 153.109.14.52 -sp 502 -ah 153.109.14.51 -ap 502 -n 2 -et 10 -ts 4 -st 1

parser = argparse.ArgumentParser(description='Simulate the content of a file over the Gridlab District')
parser.add_argument('-i','--infile', help='Input file for reading from the values (P,Q)', required=True)
parser.add_argument('-o','--outfile', help='Output file for the logging values, (current,voltage,...)', required=False)

parser.add_argument('-d','--district', help='Specify the district letter', required=True)

parser.add_argument('-dt','--deltatime', help='Time interval for the simulation', required=True)
parser.add_argument('-rt','--runtime', help='Total run time', required=True)
parser.add_argument('-t','--realtime', help='Real time for the simulation', required=True)

args = vars(parser.parse_args())
print os.getcwd()

if 'outfile' not in args.keys() or args['outfile'] == None:
    args['outfile'] = os.getcwd() + '\log.csv'

readparam = [ParamType.un1_PA,ParamType.un1_QA,ParamType.un2_PA,ParamType.un2_QA,ParamType.un3_PA,ParamType.un3_QA,ParamType.un5_PA,ParamType.un5_QA,
             ParamType.un1_U1, ParamType.un1_U2, ParamType.un1_U3,
             ParamType.un1_I1, ParamType.un1_I2, ParamType.un1_I3,
             ParamType.un2_U1, ParamType.un2_U2, ParamType.un2_U3,
             ParamType.un2_I1, ParamType.un2_I2, ParamType.un2_I3,
             ParamType.un3_U1, ParamType.un3_U2, ParamType.un3_U3,
             ParamType.un3_I1, ParamType.un3_I2, ParamType.un3_I3,
             ParamType.un5_U1, ParamType.un5_U2, ParamType.un5_U3,
             ParamType.un5_I1, ParamType.un5_I2, ParamType.un5_I3]

writeparam = [ParamType.un1_P, ParamType.un1_Q,
                   ParamType.un2_P, ParamType.un2_Q,
                   ParamType.un3_P, ParamType.un3_Q]

pqfilereader = PQFileReader('pqfilereader', args['infile'],
                            args['outfile'],
                            readparam, writeparam)
pqfilereader.initFile()

gridunit1 = GridLabCyberPhysicalSystem("gridlabcyberphysicalsystemunit1")

# readgridlabunit1 = [ParamType.un1_U1, ParamType.un1_U2, ParamType.un1_U3, ParamType.un1_UN,
#                ParamType.un1_I1, ParamType.un1_I2, ParamType.un1_I3, ParamType.un1_IN,
#                ParamType.un1_UL12, ParamType.un1_UL23, ParamType.un1_UL31,
#                ParamType.un1_USUM, ParamType.un1_ISUM,
#                ParamType.un1_PL1, ParamType.un1_PL2, ParamType.un1_PL3, ParamType.un1_PA,
#                ParamType.un1_QL1, ParamType.un1_QL2, ParamType.un1_QL3, ParamType.un1_QA,
#                ParamType.un1_SL1, ParamType.un1_SL2, ParamType.un1_SL3, ParamType.un1_SA]
# readregisterunit1 = {'all': 40201, 'quantity': ParamType.getQuantity()}
writegridlabunit1 = [(ParamType.un1_P, SumAggregator(), PConverter(-10000,10000)),
                     (ParamType.un1_Q, SumAggregator(), QConverter(-10000,10000))]
# writeregisterunit1 = {ParamType.un1_P: 1066 - 1, ParamType.un1_Q: 1063 - 1} #1-2 drive

#gridunit1.initialize('b',1,readgridlabunit1, readregisterunit1, int(args['number'] + '1'), writegridlabunit1, writeregisterunit1) #sicam on 2 drive
gridunit1.initialize(args['district'],1,writeparamlist=writegridlabunit1)
gridunit1.add(pqfilereader)

gridunit2 = GridLabCyberPhysicalSystem("gridlabcyberphysicalsystemunit2")

writegridlabunit2 = [(ParamType.un2_P, SumAggregator(), PConverter(-10000,10000)),
                     (ParamType.un2_Q, SumAggregator(), QConverter(-10000,10000))]
gridunit2.initialize(args['district'],2,writeparamlist=writegridlabunit2)
gridunit2.add(pqfilereader)

gridunit3 = GridLabCyberPhysicalSystem("gridlabcyberphysicalsystemunit3")

writegridlabunit3 = [(ParamType.un3_P, SumAggregator(), PConverter(-10000,10000)),
                     (ParamType.un3_Q, SumAggregator(), QConverter(-10000,10000))]
gridunit3.initialize(args['district'],3,writeparamlist=writegridlabunit3)
gridunit3.add(pqfilereader)

gridunit5 = GridLabCyberPhysicalSystem("gridlabcyberphysicalsystemunit5")

gridunit5.initialize(args['district'],5)
gridunit5.add(pqfilereader)

Simulator.register_simulation_module(CyberPhysicalModule)
Simulator.register_simulation_module(MinimalCyberPhysicalModule)

sim = Simulator(RealTimeExecutionManager(int(args['realtime']) * units.seconds))

sim.cyberphysicalmodule.add(gridunit1)
sim.cyberphysicalmodule.add(gridunit2)
sim.cyberphysicalmodule.add(gridunit3)
sim.cyberphysicalmodule.add(gridunit5)

sim.minimalcyberphysicalmodule.add(pqfilereader)

sim.reset()
print('start simulation')
sim.run(int(args['runtime']) * units.seconds, int(args['deltatime']) * units.seconds)
print('end simulation')