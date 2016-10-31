"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.simulation import Simulator
from gridsim.execution import RealTimeExecutionManager

from gridsim.cyberphysical.simulation import CyberPhysicalModule
from gridsim.cyberphysical.element.gridlab import GridLabCyberPhysicalSystem

from gridsim.cyberphysical.element.pqcontroller import PQController

from gridsim.cyberphysical.element.aggregator import SumAggregator
from gridsim.cyberphysical.element.converter import PConverter, QConverter

from paramtype import ParamType

from gridsim.unit import units

import argparse
import os

#Example of a user input terminal reader using the cyber-physical module with the following starting params
# -sh 153.109.14.52 -sp 502 -ah 153.109.14.51 -ap 502 -n 2 -et 10 -ts 4 -st 1

parser = argparse.ArgumentParser(description='Simulate the content of a file over the Gridlab District')
parser.add_argument('-o','--outfile', help='Output file for the logging values, (current,voltage,...)', required=False)

parser.add_argument('-d','--district', help='Specify the district number', required=True)

parser.add_argument('-dt','--deltatime', help='Time interval for the simulation', required=True)
parser.add_argument('-rt','--runtime', help='Total run time', required=True)
parser.add_argument('-t','--realtime', help='Real time for the simulation', required=True)

args = vars(parser.parse_args())
print os.getcwd()

if 'outfile' not in args.keys() or args['outfile'] == None:
    args['outfile'] = os.getcwd() + '\log.csv'

readparam = [ParamType.un1_QA,ParamType.un1_PA]

writeparam = [ParamType.un1_P, ParamType.un1_Q,
                   ParamType.un2_P, ParamType.un2_Q,
                   ParamType.un3_P, ParamType.un3_Q]

pqcontroller = PQController(readparam, writeparam)

pqcontroller.initConsole()

gridunit1 = GridLabCyberPhysicalSystem("gridlabcyberphysicalsystemunit1")

writegridlabunit1 = [(ParamType.un1_P,SumAggregator(),PConverter(-32768,32768)),
                     (ParamType.un1_Q,SumAggregator(),QConverter(-32768,32768))]

gridunit1.initialize(args['district'],1,writeparamlist=writegridlabunit1)
gridunit1.add(pqcontroller)

Simulator.register_simulation_module(CyberPhysicalModule)

sim = Simulator(RealTimeExecutionManager(int(args['realtime']) * units.seconds))

sim.cyberphysicalmodule.add(gridunit1)

sim.reset()
print('start simulation')
sim.run(int(args['runtime']) * units.seconds, int(args['deltatime']) * units.seconds)
print('end simulation')