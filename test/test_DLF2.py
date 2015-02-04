# This is a test program for the DirectLoadFlowCalculator present in the
# gridsim.electricalnetwork module. It computes the example given in
# http://home.eng.iastate.edu/~jdm/ee553/DCPowerFlowEquations.pdf pp. 10-15 and
# compare results with those of the reference.

import unittest
import numpy as np

from gridsim.electrical.loadflow import DirectLoadFlowCalculator


class TestDLF2(unittest.TestCase):

    def test_reference(self):

        # network set-up
        #----------------
        # boolean array specifying which bus is a PV bus
        # has to be a one-dimensional boolean numpy array
        is_PV = np.array([False,True,False,True])

        # array giving from-bus and to-bus ids for each branch
        # b12, b13, b14, b23, b34
        b = np.array([[0, 1], [0, 2], [0, 3], [1, 2], [2, 3]])

        # array containing branch admittances
        Yb = np.zeros((5,4),dtype=complex)
        yT = [1j*(-10.), 1j*(-10.), 1j*(-10.), 1j*(-10.), 1j*(-10.)]
        for i_branch in range(0, 5):
            Yb[i_branch, 0] = yT[i_branch]
            Yb[i_branch, 1] = yT[i_branch]
            Yb[i_branch, 2] = yT[i_branch]
            Yb[i_branch, 3] = yT[i_branch]

        # calculator initialization
        #--------------------------
        s_base = 1.0
        v_base = 1.0
        dlf = DirectLoadFlowCalculator()
        #dlf = NewtonRaphsonLoadFlowCalculator()
        dlf.update(s_base, v_base, is_PV, b, Yb)

        # input buses electrical values
        #------------------------------
        # P, Q, V, Th can be either numpy 1-D arrays or 2-D arrays with 1 row,
        # respectively 1 column

        # P1,P2,P3,P4, slack power can be set to any value, e.g. float('NaN')
        P = np.array([float('NaN'), 2.-1., -4., 1.])
        Q = np.array([float('NaN'), 0., 0., 0.])
        # mutable variable is needed
        V = np.ones([4])
        # mutable variable is needed
        Th = np.zeros([4])

        # compute buses other electrical values
        #--------------------------------------
        [P, Q, V, Th] = dlf.calculate(P, Q, V, Th, True)

        # check results against reference values
        p_slack = P[0]
        # print "P_slack ="
        # print p_slack
        refslack = 2.

        self.assertEqual(p_slack, refslack, "The power of the slack bus is "
                         + str(p_slack) + " instead of " + str(refslack))

        # print "Th = "
        # print Th
        ref_Th = np.array([0., -0.025, -0.15, -0.025])  # Th1,Th2,Th3,Th4
        self.assertTrue(np.allclose(Th, ref_Th))

        # get branch currents
        #---------------------------------
        [Pij, Qij, Pji, Qji] = dlf.get_branch_power_flows(True)

        # check results against reference values
        # print "Pij = "
        # print Pij
        # P12,P13,P14, P23,P34
        ref_Pij = np.array([0.25, 1.5, 0.25, 1.25, -1.25])

        self.assertTrue(np.allclose(Pij, ref_Pij))

if __name__ == '__main__':
    unittest.main()