# This program checks whether the default DirectLoadFlowCalculator present in
# the gridsim.electrical module performs correctly. It computes the example
# given in Hossein Seifi, Mohammad Sadegh Sepasian, Electric Power System
# Planning: Issues, Algorithms and Solutions, pp. 247-248 and compare results
# with those of the reference.
#
# Example input:
#     _                                        _
#   /   \                                    /   \
#  |    |                                   |    |
#  \   /                                    \   /
#    +    -------------------------------     +
#    |    |                             |     |
#  --+----+--                         --+-----+--
#         |                             |
#         |                             |
#         |                             |
#         -------------     -------------
#                     |     |
#                   --+--+--+--
#                        |
#                        V
# Loads and generations
#-------------------------------------------------------------------
# Bus number    Bus type       PD (MW)      QD (MVAr)   PG (MW)
#-------------------------------------------------------------------
# 1             Slack           0           0           Unknown
# 2             PV              10          5           63
# 3             PQ              90          30          0
#-------------------------------------------------------------------
#
# Branches
#-------------------------------------------------------------------
# Line number   From bus        To bus      X (p.u.)    Rating (MVA)
#-------------------------------------------------------------------
# 1             1               2           0.0576      250
# 2             2               3           0.092       250
# 3             1               3           0.17        150
#-------------------------------------------------------------------

import unittest

import numpy as np

from gridsim.simulation import Simulator
from gridsim.unit import units
from gridsim.electrical.network import ElectricalPVBus, ElectricalPQBus, \
    ElectricalTransmissionLine, ElectricalSlackBus
from gridsim.electrical.element import ConstantElectricalCPSElement
from gridsim.electrical.core import ElectricalNetworkBranch
from gridsim.recorder import PlotRecorder

from gridsim.electrical.loadflow import DirectLoadFlowCalculator


class TestEsimDLF(unittest.TestCase):

    def test_reference(self):

        # Initialize the Gridsim simulator and get a reference to
        # its electrical part
        sim = Simulator()
        esim = sim.electrical
        esim.load_flow_calculator = DirectLoadFlowCalculator()

        # network initialization
        #----------------------

        # add buses to simulator
        # slack bus has been automatically added
        bus1 = esim.bus('Slack Bus')
        bus2 = esim.add(ElectricalPVBus('Bus 2'))
        bus3 = esim.add(ElectricalPQBus('Bus 3'))

        # add branches to simulator
        # line length is arbitrarily set to 1.0
        bra1 = esim.connect('Branch 1-2', esim.bus('Slack Bus'),
                            esim.bus('Bus 2'),
                            ElectricalTransmissionLine('Line 1',
                            1.0*units.metre, 0.0576*units.ohm))
        # line length is arbitrarily set to 1.0
        bra2 = esim.connect('Branch 2-3', esim.bus('Bus 2'),
                            esim.bus('Bus 3'),
                            ElectricalTransmissionLine('Line 2',
                            1.0*units.metre, 0.092*units.ohm))
        # line length is arbitrarily set to 1.0
        bra3 = esim.connect('Branch 1-3', esim.bus('Slack Bus'),
                            esim.bus('Bus 3'),
                            ElectricalTransmissionLine('Line 3',
                            1.0*units.metre, 0.17*units.ohm))

        # input buses electrical values
        #------------------------------
        esim.attach('Bus 2', ConstantElectricalCPSElement('GD2', -.53*units.watt))
        esim.attach('Bus 3', ConstantElectricalCPSElement('GD3', .9*units.watt))

        # create recorders to collect output data
        #-----------------------------------------
        # Create a plot recorder which records active power on slack bus.
        bus_pwr = PlotRecorder('P', units.second, units.watt)
        sim.record(bus_pwr, esim.find(element_class=ElectricalSlackBus))
        # Create a plot recorder which records theta angle on each bus.
        bus_th = PlotRecorder('Th', units.second, units.radian)

        sim.record(bus_th, esim.find(has_attribute='Th'))

        # Create a plot recorder which records power flow on each branch.
        bra_pwr = PlotRecorder('Pij', units.second, units.watt)

        sim.record(bra_pwr, esim.find(element_class=ElectricalNetworkBranch))

        # make one simulation step
        #-------------------------
        sim.reset()

        sim.step(1*units.second)

        # get values stored by recorders
        # and compare them with references
        #----------------------------------
        # slack active power

        y = bus_pwr.y_values()
        p_slack = y[bus1.friendly_name][0]

        refslack = 0.37

        self.assertEqual(p_slack, refslack, "The power of the slack bus is "
                         + str(p_slack) + " instead of " + str(refslack))

        y = bus_th.y_values()
        # theta angles of all buses
        th = np.array([y[bus1.friendly_name][0],
                       y[bus2.friendly_name][0],
                       y[bus3.friendly_name][0]])

        ref_th = np.array([0., -0.00254839, -0.05537872])

        for ith, iref_th in zip(th, ref_th):
            self.assertAlmostEqual(ith, iref_th)

        # power flows of all branches
        y = bra_pwr.y_values()
        pbr = np.array([y[bra1.friendly_name][0],
                        y[bra2.friendly_name][0],
                        y[bra3.friendly_name][0]])
        ref_pbr = np.array([0.044243, 0.574243, 0.325757])

        self.assertTrue(np.allclose(pbr, ref_pbr),
                        "The power of the slack bus is " + str(p_slack) +
                        " instead of " + str(refslack))

if __name__ == '__main__':
    unittest.main()