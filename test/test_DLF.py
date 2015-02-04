# This is a test program for the DirectLoadFlowCalculator present in the
# gridsim.electricalnetwork module. It computes the example given in Hossein
# Seifi, Mohammad Sadegh Sepasian, Electric Power System Planning: Issues,
# Algorithms and Solutions, pp. 247-248 and compare results with those of
# the reference.
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

from gridsim.electrical.loadflow import DirectLoadFlowCalculator


class TestDLF(unittest.TestCase):

    def test_reference(self):

        # network set-up
        #----------------
        # boolean array specifying which bus is a PV bus
        # has to be a one-dimensional boolean numpy array
        is_PV = np.array([False, True, False])


        # array giving from-bus and to-bus ids for each branch
        b = np.array([[0, 1], [1, 2], [0, 2]])

        # array containing branch admittances
        Yb = np.zeros((3,4), dtype=complex)
        yT = [1./(1j*0.0576), 1./(1j*0.092), 1./(1j*0.17)]
        for i_branch in range(0, 3):
            Yb[i_branch, 0] = yT[i_branch]
            Yb[i_branch, 1] = yT[i_branch]
            Yb[i_branch, 2] = yT[i_branch]
            Yb[i_branch, 3] = yT[i_branch]

        # calculator initialization
        #--------------------------

        # set to 1.0 instead of 100.0e+06 since Yb is already in per unit
        s_base = 1.0
        v_base = 1.0
        dlf = DirectLoadFlowCalculator()
        #dlf = NewtonRaphsonLoadFlowCalculator()
        dlf.update(s_base, v_base, is_PV, b, Yb)

        # input buses electrical values
        #------------------------------
        # P, Q, V, Th can be either numpy 1-D arrays or 2-D arrays with 1 row,
        # respectively 1 column

        # slack power can be set to any value, e.g. float('NaN')
        P = np.array([float('NaN'), 0.63-0.1, -0.9])
        # slack power can be set to any value, e.g. float('NaN')
        Q = np.array([float('NaN'), -0.05, -0.3])
        # mutable variable is needed
        V = np.ones([3])
        # mutable variable is needed
        Th = np.zeros([3])

        # compute buses other electrical values
        #--------------------------------------
        [P, Q, V, Th] = dlf.calculate(P, Q, V, Th, True)

        # check results against reference values
        P_slack = P[0]
        # print "P_slack ="
        # print P_slack
        refslack = 0.37

        self.assertEqual(P_slack, refslack)

        # print "Th = "
        # print Th
        ref_Th = np.array([0., -0.00254839, -0.05537872])

        self.assertTrue(np.allclose(Th, ref_Th))

        # get branch currents
        #---------------------------------
        [Pij, Qij, Pji, Qji] = dlf.get_branch_power_flows(True)

        # check results against reference values
        Pbr = Pij
        # print "Pbr = "
        # print Pbr
        ref_Pbr = np.array([0.044243, 0.574243, 0.325757])

        self.assertTrue( np.allclose(Pbr,ref_Pbr) )

if __name__ == '__main__':
    unittest.main()
