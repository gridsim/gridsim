import unittest
import math
import numpy as np

from gridsim.electrical.loadflow import NewtonRaphsonLoadFlowCalculator


class TestNRLF5Bus(unittest.TestCase):

    def test_reference(self):

        # Network setup
        # =============
        # buses
        # -----
        is_PV = np.array([False, False, False, False, True])

        # branches
        # --------
        b = np.array([
        [0, 3],
        [1, 2],
        [1, 3],
        [2, 3],
        [4, 2]
        ])

        # admittances in all branches
        Y_T = np.array([
            1.0/(1j*0.03),
            1.0/(0.04+1j*0.25),
            1.0/(0.1+1j*0.35),
            1.0/(0.08+1j*0.3),
            1.0/(1j*0.015)])

        # check
        self.assertEqual(len(Y_T), b.shape[0])

        # transformers
        is_transformer = np.array([True, False, False, False, True])
        k_T = np.array([1.05+0j, 1.05+0j])

        # check
        self.assertEqual(sum(is_transformer), len(k_T))

        # transmission lines
        iterable = (not i for i in is_transformer)
        is_line = np.fromiter(iterable, np.bool)
        b_L = np.array([0.5, 0., 0.5])

        # check
        self.assertEqual(sum(is_line), len(b_L), "the length of " +
                        str(b_L) + " is " + str(len(b_L)) + " instead of " +
                        str(sum(is_line)))

        # compute branch admittances
        Yb = np.zeros([b.shape[0], 4], dtype=complex)

        # transformers
        Yb[is_transformer, 0] = Y_T[is_transformer]
        Yb[is_transformer, 1] = Y_T[is_transformer]/k_T
        Yb[is_transformer, 2] = Y_T[is_transformer]/(abs(k_T)**2)
        Yb[is_transformer, 3] = Y_T[is_transformer]/k_T.conjugate()

        # transmission lines
        Yb[is_line, 0] = Y_T[is_line]+1j*b_L/2
        Yb[is_line, 1] = Y_T[is_line]
        Yb[is_line, 2] = Y_T[is_line]+1j*b_L/2
        Yb[is_line, 3] = Y_T[is_line]

        # initialize Newton-Raphson Load flow calculator
        # ==============================================
        s_base = 1.
        v_base = 1.
        nrlf = NewtonRaphsonLoadFlowCalculator(s_base, v_base, is_PV, b, Yb)

        # inputs
        # ======
        # bus active powers
        P = np.array([float('NaN'), -1.6, -2.0, -3.7, 5.0])
        # bus reactive powers
        Q = np.array([float('NaN'), -0.8, -1., -1.3, float('NaN')])
        # bus voltage amplitudes, values for PQ buses are set arbitrarily
        # to NaN, can be any value
        V = np.array([1.05, float('NaN'), float('NaN'), float('NaN'), 1.05])
        # bus voltage angles
        Th = np.zeros([5])  # mutable variable is needed

        # use Newton-Raphson Load flow calculator to calculate missing bus
        # electrical values
        # ======================================================================
        [P, Q, V, Th] = nrlf.calculate(P, Q, V, Th, True)

        # output results, compare with reference values and output comparison
        # results (OK / NOT OK)
        # ======================================================================
        P_slack = P[0]
        refslack = 2.5795

        self.assertTrue(abs(P_slack-refslack)-1e-4)

        ref_Q = np.array([2.2995, -0.8, -1.0, -1.3, 1.8134])

        self.assertTrue(np.allclose(Q, ref_Q, 1.e-3))

        ref_V = np.array([1.05, 0.86215, 1.07791, 1.03641, 1.05])

        self.assertTrue(np.allclose(V, ref_V))

        ref_Th = np.array([0., -4.77851, 17.85353, -4.28193, 21.84332])
        ref_Th = ref_Th*math.pi/180.

        for ith, iref_th in zip(Th, ref_Th):
            self.assertAlmostEqual(ith, iref_th)

        # compute branch power load flows
        # ===============================

        [Pij, Qij, Pji, Qji] = nrlf.get_branch_power_flows(True)

        # output results, compare with reference values and output comparison
        # results (OK / NOT OK)
        # ======================================================================

        ref_Pij = np.array([2.5795, -1.4664, -0.1338, 1.4157, 5.0])

        self.assertTrue(np.allclose(Pij, ref_Pij, 1.e-3))

        ref_Qij = np.array([2.2995, -0.4089, -0.3909, -0.2442, 1.8134])

        self.assertTrue(np.allclose(Qij, ref_Qij, 1.e-3))

        ref_Pji = np.array([-2.5795, 1.5848, 0.1568, -1.2775, -5.0])

        self.assertTrue(np.allclose(Pji, ref_Pji, 1.e-3))

        ref_Qji = np.array([-1.9746, 0.6727, 0.4713, 0.2033, -1.4285])

        self.assertTrue(np.allclose(Qji, ref_Qji, 1.e-3))

if __name__ == '__main__':
    unittest.main()