

import unittest
import numpy as np

from gridsim.electrical.loadflow import NewtonRaphsonLoadFlowCalculator


class TestNRLF14Bus(unittest.TestCase):

    def test_reference(self):

        # Network setup
        # =============
        # buses
        # -----
        is_PV = np.array([False, True, True, False, False, True, False, True,
                          False, False, False, False, False, False])

        # branches
        # --------
        b = np.array([
        [0, 1],
        # [0,2] in Xi-Fan Wang, Yonghua Song, Malcolm Irving, Modern
        # Power Systems Analysis, p. 174
        [0, 4],
        [1, 2],
        [1, 3],
        [1, 4],
        [2, 3],
        [3, 4],
        [3, 6],
        [3, 8],
        [4, 5],
        [5, 10],
        [5, 11],
        [5, 12],
        [6, 7],
        [6, 8],
        [8, 9],
        [8, 13],
        [9, 10],
        [11, 12],
        [12, 13]
        ])

        # admittances in all branches
        Y_T = np.array([
            1.0/(0.01938+1j*0.05917),
            1.0/(0.05403+1j*0.22304),
            1.0/(0.04699+1j*0.19797),
            1.0/(0.05811+1j*0.17632),
            1.0/(0.05695+1j*0.17388),
            1.0/(0.06701+1j*0.17103),
            1.0/(0.01335+1j*0.04211),
            1.0/(0.00000+1j*0.20912),
            1.0/(0.00000+1j*0.55618),
            1.0/(0.00000+1j*0.25202),
            1.0/(0.09498+1j*0.19890),
            1.0/(0.12291+1j*0.25581),
            1.0/(0.06615+1j*0.13027),
            1.0/(0.00000+1j*0.17615),
            1.0/(0.00000+1j*0.11001),
            1.0/(0.03181+1j*0.08450),
            1.0/(0.12711+1j*0.27038),
            1.0/(0.08205+1j*0.19207),
            1.0/(0.22092+1j*0.19988),
            1.0/(0.17093+1j*0.34802)])

        # check
        self.assertEqual(len(Y_T), b.shape[0])

        # transformers
        is_transformer = np.array([False, False, False, False, False, False,
                                   False, True, True, True, False, False, False,
                                   False, False, False, False, False, False,
                                   False], dtype=bool)
        # print is_transformer
        k_T = np.array([0.97800+0j, 0.96900+0j, 0.93200+0j])

        # check
        self.assertEqual(sum(is_transformer), len(k_T))

        # transmission lines
        iterable = (not i for i in is_transformer)
        is_line = np.fromiter(iterable, np.bool)
        b_L = np.array([
            0.0528,
            0.0492,
            0.0438,
            0.0340,
            0.0346,
            0.0128,
            0.,
            0.,
            0.,
            0.,
            0.,
            0.,
            0.,
            0.,
            0.,
            0.,
            0.])

        # check
        self.assertEqual(sum(is_line), len(b_L))

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
        P = np.array([
            2.324,0.183,
            -0.942,
            -0.478,
            -0.076,
            -0.112,
            0.0,
            0.0,
            -0.295,
            -0.090,
            -0.035,
            -0.061,
            -0.135,
            -0.149])

        # bus reactive powers
        Q = np.array([
            0.0,
            0.0,
            0.0,
            0.039,
            -0.016,
            0.0,
            0.0,
            0.0,
            0.046,
            -0.058,
            -0.018,
            -0.016,
            -0.058,
            -0.050])

        # bus voltage amplitudes, values for PQ buses are set arbitrarily to
        # NaN, can be any value
        V = np.array([
            1.06,
            1.045,
            1.01,
            float('NaN'),
            float('NaN'),
            1.07,
            float('NaN'),
            1.09,
            float('NaN'),
            float('NaN'),
            float('NaN'),
            float('NaN'),
            float('NaN'),
            float('NaN')])
        # bus voltage angles
        Th = np.ones([14])  # mutable variable is needed

        # use Newton-Raphson Load flow calculator to calculate missing bus
        # electrical values
        # ======================================================================
        [P, Q, V, Th] = nrlf.calculate(P, Q, V, Th, True)

        # output results
        # ================
        # print P[0]
        # print Q
        # print V
        # print Th*180/3.14159

if __name__ == '__main__':
    unittest.main()
