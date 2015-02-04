"""
.. moduleauthor:: Michael Sequeira Carvalho <michael.sequeira@hevs.ch>
.. moduleauthor:: Gilbert Maitre <gilbert.maitre@hevs.ch>

This module provides a toolbox to Gridsim to perform computation of electrical
values within the electrical network, in other words to solve the so-called
power-flow problem:

.. seealso::
    http://en.wikipedia.org/wiki/Power-flow_study#Power-flow_problem_formulation
"""
import numpy as np
from numpy.linalg import inv
from scipy.sparse import lil_matrix

from gridsim.decorators import accepts, returns


class AbstractElectricalLoadFlowCalculator(object):

    def __init__(self):
        """
        __init__(self)

        This class is the base for all calculator that have been or are going to
        be implemented to solve the power-flow problem.

        At initialization the user has to give the reference power value
        `s_base` (all power values are then given relative to this reference
        value), the reference voltage value `v_base` (all voltage values are
        then given relative to this reference value), a boolean array `is_PV`
        specifying which one among the buses is a :class:`.ElectricalPVBus`
        (the bus with 1st position is slack, the others non
        :class:`.ElectricalPVBus` are :class:`.ElectricalPQBus`), an integer
        array `b` specifying for each branch the bus id it is starting from and
        the bus id it is going to, a complex array `Yb` specifying
        admittances of each network branch.
        """
        super(AbstractElectricalLoadFlowCalculator, self).__init__()

        self.s_base = None
        """
        The reference power value.
        Set by :func:`AbstractElectricalLoadFlowCalculator.update`
        """
        self.v_base = None
        """
        The reference voltage value.
        Set by :func:`AbstractElectricalLoadFlowCalculator.update`
        """
        self._is_PV = None
        self._b = None
        self._Yb = None
        self._s_sc = None
        self._v_sc = None
        self._nBu = None
        self._nV = None
        self._nQ = None
        self._nBr = None
        self._is_PQ = None
        self._Y = None
        self._P = None
        self._Q = None
        self._V = None
        self._Th = None

    @accepts(((1, 2), (int, float)))
    def update(self, s_base, v_base, is_PV, b, Yb):
        """
        update(self, s_base, v_base, is_PV, b, Yb)

        Updates values of the calculator.

        :param s_base: reference power value
        :type s_base: float
        :param v_base: reference voltage value
        :type v_base: float
        :param is_PV: N-long vector specifying which bus is of type
            :class:`.ElectricalPVBus`, where N is the number of buses including
            slack.
        :type is_PV: 1-dimensional numpy array of boolean
        :param b: Mx2 table containing for each branch the ids of start and end
            buses.
        :type b: 2-dimensional numpy array of int
        :param Yb: Mx4 table containing the admittances `Yii`, `Yij`, `Yjj`,
            and `Yji` of each branch.
        :type Yb: 2-dimensional numpy array of complex

        """
        if s_base <= 0:
            raise RuntimeError(
                'Reference power value s_base cannot be zero or negative')
        if v_base <= 0:
            raise RuntimeError(
                'Reference voltage value v_base cannot be zero or negative')
        if is_PV.dtype != bool:
            raise TypeError('is_PV has to be a boolean array')
        if len(is_PV.shape) != 1:
            raise RuntimeError('is_PV has to be a one-dimensional array')
        if is_PV[0]:
            raise RuntimeError(
                'bus with 1st position is slack and therefore '
                'cannot be a PV bus')
        if b.dtype != int:
            raise TypeError('b has to be an integer array')
        if len(b.shape) != 2:
            raise RuntimeError('b has to be a two-dimensional array')
        if b.shape[1] != 2:
            raise RuntimeError('b array should have two columns')
        if Yb.dtype != complex:
            raise TypeError('array Yb has to be a complex array')
        if len(Yb.shape) != 2:
            raise RuntimeError('Yb has to be a two-dimensional array')
        if Yb.shape[1] != 4:
            raise RuntimeError('Yb array should have four columns')
        if Yb.shape[0] != b.shape[0]:
            raise RuntimeError(
                'Yb and b arrays should have the same number of rows')

        self.s_base = s_base
        self.v_base = v_base

        self._is_PV = is_PV
        self._b = b
        self._Yb = Yb

        # scaling factor corresponding to s_base
        self._s_sc = 1.0 / self.s_base
        # scaling factor corresponding to s_base
        self._v_sc = 1.0 / self.v_base
        # number of buses
        self._nBu = self._is_PV.shape[0]
        # number of PV buses
        self._nV = self._is_PV.sum()
        # number of PQ buses
        self._nQ = self._nBu - self._nV - 1
        # PQ buses positions
        self._is_PQ = ~self._is_PV
        self._is_PQ[0] = False  # the slack bus
        # number of branches
        self._nBr = self._b.shape[0]

        # scale self._Yb according to s_base and v_base
        # S = V*I = V^2*Y
        v2_base = self.v_base * self.v_base
        if self.s_base != v2_base:
            self._Yb *= (v2_base * self._Yb)

        # compute admittance matrix Y
        self._Y = np.zeros([self._nBu, self._nBu], dtype=complex)
        # off-diagonal elements
        self._Y[self._b[:, 0], self._b[:, 1]] = -self._Yb[:, 1]
        self._Y[self._b[:, 1], self._b[:, 0]] = -self._Yb[:, 3]
        # diagonal elements
        for i_branch in range(0, self._nBr):
            i_bus = self._b[i_branch, 0]
            j_bus = self._b[i_branch, 1]
            self._Y[i_bus, i_bus] += self._Yb[i_branch, 0]
            self._Y[j_bus, j_bus] += self._Yb[i_branch, 2]

        # set internal bus electrical values to None
        self._P = None
        self._Q = None
        self._V = None
        self._Th = None

    def _read_calculate_args(self, P, Q, V, Th, scaled):

        if P.dtype != float or Q.dtype != float \
                or V.dtype != float or Th.dtype != float:
            raise TypeError('input array has to be an array of floats.')

        if len(P.shape) != 1 or len(Q.shape) != 1 \
                or len(V.shape) != 1 or len(Th.shape) != 1:
            raise RuntimeError('input array has to be one-dimensional')

        if scaled:
            self._P = P.copy()
            self._Q = Q.copy()
            self._V = V.copy()
        else:
            self._P = self._s_sc * P
            self._Q = self._s_sc * Q
            self._V = self._v_sc * V

    @accepts((5, bool))
    def calculate(self, P, Q, V, Th, scaled):
        """
        calculate(self, P, Q, V, Th, scaled)

        Compute all bus electrical values determined by the network:

        - takes as input active powers P of all non-slack buses, reactive powers
          of :class:`.ElectricalPQBus` and voltage amplitudes of
          :class:`.ElectricalPVBus`; all these values have to be placed by the
          user at the right place in the N-long vectors, `P`, `Q`, and,
          respectively, `V`, passed to this method.

        - outputs active power of slack bus, reactive powers of
          :class:`.ElectricalPVBus`, voltage amplitudes of
          :class:`.ElectricalPQBus`, and voltage angles of all buses; all these
          values are placed by this method at the
          right place in the N-long vectors `P`, `Q`, `V`, and, respectively,
          `Th`, passed to this method.

        :param P: N-long vector of bus active powers, where N is the number of
            buses including slack.
        :type P: 1-dimensional numpy array of float

        :param Q: N-long vector of bus reactive powers, where N is the number of
            buses including slack.
        :type Q: 1-dimensional numpy array of float

        :param V: N-long vector of bus voltage amplitudes, where N is the number
            of buses including slack.
        :type V: 1-dimensional numpy array of float

        :param Th: N-long vector of bus voltage angles, where N is the number
            of buses including slack.
        :type Th: 1-dimensional numpy array of float

        :param scaled: specifies whether electrical input values are scaled or
            not
        :type scaled: boolean

        :return: modified [P, Q, V, Th]
        :rtype: a list of 4 element
        """
        raise NotImplementedError('Pure abstract method!')

    @accepts((1, bool))
    @returns(tuple)
    def get_branch_power_flows(self, scaled):
        """
        get_branch_power_flows(self, scaled)

        Compute all branch power flows. Cannot be called before method
        :func:`AbstractElectricalLoadFlowCalculator.calculate`.
        Returns a tuple made of 4 1-dimensional numpy arrays:

        - Pij containing branch input active powers,
        - Qij containing branch input reactive powers,
        - Pji containing branch output active powers,
        - Qji containing branch output reactive powers.

        :param scaled: specifies whether output power flows have to be scaled or
               not
        :type scaled: boolean

        :returns: 4 M-long vector, where M is the number of branches

            :Pij: vector of active powers entering the branch from the from-bus
                  termination
            :Qij: vector of reactive powers entering the branch from the from-bus
                  termination
            :Pji: vector of active powers entering the branch from the to-bus
                  termination
            :Qji: vector of reactive powers entering the branch from the to-bus
                  termination

        :rtype: tuple of one-dimensional numpy arrays of float
        """
        # compute partial results
        ViVj = self._V[self._b[:, 0]] * self._V[self._b[:, 1]]
        dThij = self._Th[self._b[:, 0]] - self._Th[self._b[:, 1]]
        e_j_dThij = np.exp(1j * dThij)

        # branch flow from from-bus terminal
        Vi2 = self._V[self._b[:, 0]] * self._V[self._b[:, 0]]
        e_j_dThij_Yij_ = e_j_dThij * np.conjugate(self._Yb[:, 1])
        Pij = Vi2 * np.real(self._Yb[:, 0]) - ViVj * np.real(e_j_dThij_Yij_)
        Qij = Vi2 * (-np.imag(self._Yb[:, 0])) - ViVj * np.imag(e_j_dThij_Yij_)

        # branch flow from to-bus terminal
        Vj2 = self._V[self._b[:, 1]] * self._V[self._b[:, 1]]
        e_j_dThji_Yji_ = np.conjugate(e_j_dThij) * np.conjugate(self._Yb[:, 3])
        Pji = Vj2 * np.real(self._Yb[:, 2]) - ViVj * np.real(e_j_dThji_Yji_)
        Qji = Vj2 * (-np.imag(self._Yb[:, 2])) - ViVj * np.imag(e_j_dThji_Yji_)

        # TODO:verify

        if not scaled:
            Pij *= self.s_base
            Qij *= self.s_base
            Pji *= self.s_base
            Qji *= self.s_base

        return Pij, Qij, Pji, Qji


    @accepts((1, bool))
    def get_branch_max_currents(self, scaled):
        """
        get_branch_max_currents(self, scaled)

        Compute the maximal current amplitude of each branch. Cannot be called
        before method :func:`AbstractElectricalLoadFlowCalculator.calculate`.
        Returns a M-long vector of maximal branch
        current amplitudes, where M is the number of branches.

        :param scaled: specifies whether output currents have to be scaled or
            not
        :type scaled: boolean

        :returns: M-long vector containing for each branch the maximal current
            amplitude
        :rtype: 1-dimensional numpy array of float

        """
        # from-bus bus complex voltage (amplitude and phase)
        Vi_c = self._V[self._b[:, 0]] * np.exp(1j * self._Th[self._b[:, 0]])
        # current to ground at from-bus bus
        Ii0_c = Vi_c * (self._Yb[:, 0] - self._Yb[:, 1])

        # to-bus bus complex voltage (amplitude and phase)
        Vj_c = self._V[self._b[:, 1]] * np.exp(1j * self._Th[self._b[:, 1]])
        # current to ground at to-bus bus
        Ij0_c = Vj_c * (self._Yb[:, 2] - self._Yb[:, 3])

        # traversing current
        Iij_c = (Vi_c - Vj_c) * self._Yb[:, 1]

        Imax = np.max(np.hstack(abs(Ii0_c), abs(Ij0_c), abs(Ii0_c + Iij_c),
                                abs(Ij0_c - Iij_c), abs(Iij_c)), axis=1)

        # TODO:verify
        if not scaled:
            Imax = Imax * self.s_base * self.v_sc

        return Imax


class DirectLoadFlowCalculator(AbstractElectricalLoadFlowCalculator):

    @accepts(((1, 2), (int, float, type(None))))
    def __init__(self, s_base=None, v_base=None, is_PV=None, b=None, Yb=None):
        """
        This class implements the direct load flow method to solve the
        power-flow problem.

        .. seealso:: http://en.wikipedia.org/wiki/Power-flow_study#Power-flow_problem_formulation.

        The method is described for example in Hossein Seifi, Mohammad Sadegh
        Sepasian, Electric Power System Planning: Issues, Algorithms and
        Solutions, pp. 246-248

        At initialization the user has to give the reference power value
        `s_base` (all power values are then given relative to this reference
        value), the reference voltage value `v_base` (all voltage values are
        then given relative to this reference value), a boolean array `is_PV`
        specifying which one among the buses is a :class:`.ElectricalPVBus`
        (the bus with 1st position is slack, the others non
        :class:`.ElectricalPVBus` buses are :class:`.ElectricalPQBus` buses), an
        integer array `b` specifying for each branch the bus id it is starting
        from and the bus id it is going to, a complex array `Yb` specifying
        admittances of each network branch.
        """
        super(DirectLoadFlowCalculator, self).__init__()

        self._invBvq = None
        self._bA = None

        if s_base is not None and v_base is not None and is_PV is not None \
                and b is not None and Yb is not None:
            self.update(s_base, v_base, is_PV, b, Yb)

    @accepts(((1, 2), (int, float)))
    def update(self, s_base, v_base, is_PV, b, Yb):
        """
        update(self, s_base, v_base, is_PV, b, Yb)

        Updates values of the calculator.

        :param s_base: reference power value
        :type s_base: float
        :param v_base: reference voltage value
        :type v_base: float
        :param is_PV: N-long vector specifying which bus is of type
            :class:`.ElectricalPVBus`, where N is the number of buses including
            slack.
        :type is_PV: 1-dimensional numpy array of boolean
        :param b: Mx2 table containing for each branch the ids of start and end
            buses.
        :type b: 2-dimensional numpy array of int
        :param Yb: Mx4 table containing the admittances Yii, Yij, Yjj, and Yji
            of each branch.
        :type Yb: 2-dimensional numpy array of complex

        .. note:: variable names have been chosen to match the notation used in
                  Hossein Seifi, Mohammad Sadegh Sepasian, Electric Power System
                  Planning: Issues, Algorithms and Solutions, pp. 246-248
        """
        super(DirectLoadFlowCalculator, self).update(s_base, v_base,
                                                     is_PV, b, Yb)



        # compute matrix B from admittance matrix Y
        # off-diagonal elements are equal to minus imaginary part of Y elements
        B = -np.imag(self._Y)
        # diagonal elements are equal to minus sum of off-diagonal elements
        np.fill_diagonal(B, np.zeros(B.shape[0]))
        np.fill_diagonal(B, -B.sum(1))
        # compute inverse of B after removing first row and first column
        # (corresponding to slack bus)
        self._invBvq = np.linalg.inv(B[1:, 1:])

        # build bA matrix from branch susceptances as sparse matrix
        self._bA = lil_matrix((self._nBr, self._nBu))

        for i_branch in range(0, self._nBr):
            # this is minus the susceptance value
            mb = B[self._b[i_branch, 0], self._b[i_branch, 1]]
            self._bA[i_branch, self._b[i_branch, 0]] = -mb
            self._bA[i_branch, self._b[i_branch, 1]] = mb

        # change sparse matrix representation
        self._bA = self._bA.tocsr()

    @accepts((5, bool))
    def calculate(self, P, Q, V, Th, scaled):
        """
        calculate(self, P, Q, V, Th, scaled)

        Computes all bus electrical values determined by the network, i.e

        - takes as input active powers P of all non-slack buses.
        - outputs voltage angles of all buses.

        Reactive powers and voltage amplitudes are not used. However, to be
        compatible with the N-long vectors with the method of the base class,
        all N-long vectors P, Q, V, and Th have to be passed to this method.

        :param P: N-long vector of bus active powers, where N is the number of
            buses including slack.
        :type P: 1-dimensional numpy array of float
        :param Q: N-long vector of bus reactive powers, where N is the number of
            buses including slack.
        :type Q: 1-dimensional numpy array of float
        :param V: N-long vector of bus voltage amplitudes, where N is the number
            of buses including slack.
        :type V: 1-dimensional numpy array of float
        :param Th: N-long vector of bus voltage angles, where N is the number of
            buses including slack.
        :type Th: 1-dimensional numpy array of float
        :param scaled: specifies whether electrical input values are scaled or
            not
        :type scaled: boolean

        :return: modified [P, Q, V, Th]
        :rtype: a list of 4 element
        """
        # check input arguments and save them to internal
        # variables _P, _Q, and _V
        # variables _P, _Q, and _V
        self._read_calculate_args(P, Q, V, Th, scaled)
        # initialize voltage angles internal variable _Th to 0.0
        self._Th = np.zeros([self._nBu, 1])

        # compute slack active power (based on the assumption that there are no
        # branch losses)

        # update intern variable
        self._P[0] = -sum(self._P[1:])
        # update external variable
        if scaled:
            P[0] = self._P[0]
        else:
            P[0] = self.s_base * self._P[0]

        # TODO: decide if Q and V should be updated to be consistent
        # TODO (V should be set to ones)

        # vector of voltage angles
        # update intern variable
        self._Th = np.concatenate(([0.0], np.dot(self._invBvq, self._P[1:])))


        # return external variable
        self._calculate_done = True

        return [self._P, self._Q, self._V, self._Th]

    @accepts((1, bool))
    def get_branch_power_flows(self, scaled):
        """
        get_branch_power_flows(self, scaled)

        Computes all branch power flows. Cannot be called before method
        :func:`AbstractElectricalLoadFlowCalculator.calculate`.
        To be compatible with the generic method, returns a
        tuple made of 4 1-dimensional numpy arrays:

        - `Pij` containing branch input active powers,
        - `Qij` containing branch input reactive powers,
        - `Pji` containing branch output active powers,
        - `Qji` containing branch output reactive powers.

        Here, `Qij` and `Qji` are `None`. `Pji` is equal to `-Pij`.

        :param scaled: specifies whether output power flows have to be scaled
            or not
        :type scaled: boolean
        :returns: 4 M-long vector, where M is the number of branches

            :Pij: vector of active powers entering the branch from the from-bus
                  termination
            :Qij: None
            :Pji: vector of active powers entering the branch from the to-bus
                  termination
            :Qji: None

        :rtype: mixed tuple of None and one-dimensional numpy arrays of float
        """
        if self._P is None:
            # calculate has not been called
            raise RuntimeError('The calculate method has to be called first!')

        # branch active powers
        Pbr = self._bA.dot(self._Th)

        if not scaled:
            Pbr *= self.s_base

        return Pbr, None, -Pbr, None

    @accepts((1, bool))
    def get_branch_max_currents(self, scaled):
        """
        get_branch_max_currents(self, scaled)

        Returns active powers entering the branch from the from-bus termination.

        :param scaled: specifies whether output power flows have to be scaled
            or not
        :type scaled: boolean
        :returns: a M-long vector of active powers entering the branch from the
                  from-bus termination, where M is the number of branches

        .. warning:: This function is currently untested.
        """

        if self._P is None:
            # calculate has not been called
            raise RuntimeError('The calculate method has to be called first!')

        # it can be shown that in per unit the branch current magnitude is equal
        # to the branch active power (Vk~=1.0)

        # branch active powers
        [Pbr, _, _, _] = self.get_branch_power_flows(True)
        Ibr = Pbr  # FIXME Pij or Pji ???

        if not scaled:
            Ibr *= (self.s_base * self.v_sc) #

        return Ibr


class NewtonRaphsonLoadFlowCalculator(AbstractElectricalLoadFlowCalculator):

    @accepts(((1, 2), (int, float)))
    def __init__(self, s_base=None, v_base=None, is_PV=None, b=None, Yb=None):
        """
        This class implements the Newton-Raphson method to solve the power-flow
        problem.

        .. seealso::
            http://en.wikipedia.org/wiki/Power-flow_study#Power-flow_problem_formulation.

        At initialization the user has to give the reference power value
        `s_base` (all power values are then given relative to this reference
        value), the reference voltage value `v_base` (all voltage values are
        then given relative to this reference value), a boolean array `is_PV`
        specifying which one among the buses is a :class:`.ElectricalPVBus`
        (the bus with 1st position is slack, the others non
        :class:`.ElectricalPVBus` are :class:`.ElectricalPQBus`), an integer
        array `b` specifying for each branch the bus id it is starting from and
        the bus id it is going to, a complex array `Yb` specifying
        admittances of each network branch.
        """
        super(NewtonRaphsonLoadFlowCalculator, self).__init__()

        self._G = None
        self._B = None
        self._residual_metric = None
        self._residual_tolerance = None
        self._ones_vector = None

        if s_base is not None and v_base is not None and is_PV is not None \
                and b is not None and Yb is not None:
            self.update(s_base, v_base, is_PV, b, Yb)

    @accepts(((1, 2), (int, float)))
    def update(self, s_base, v_base, is_PV, b, Yb):
        """
        update(self, s_base, v_base, is_PV, b, Yb)

        Updates values of the calculator.

        :param s_base: reference power value
        :type s_base: float
        :param v_base: reference voltage value
        :type v_base: float
        :param is_PV: N-long vector specifying which bus is of type
            :class:`.ElectricalPVBus`, where N is the number of buses including
            slack.
        :type is_PV: 1-dimensional numpy array of boolean
        :param b: Mx2 table containing for each branch the ids of start and end
            buses.
        :type b: 2-dimensional numpy array of int
        :param Yb: Mx4 table containing the admittances `Yii`, `Yij`, `Yjj`,
            and `Yji` of each branch.
        :type Yb: 2-dimensional numpy array of complex
        """
        super(NewtonRaphsonLoadFlowCalculator, self).update(s_base, v_base,
                                                            is_PV, b, Yb)

        # compute real part and imaginary part of admittance matrix
        self._G = np.real(self._Y)
        self._B = np.imag(self._Y)

        self._residual_metric = 1
        self._residual_tolerance = 1e-12
        self._ones_vector = np.ones(self._nBu)

    @accepts((5, bool))
    def calculate(self, P, Q, V, Th, scaled):
        """
        calculate(self, P, Q, V, Th, scaled)

        Compute all bus electrical values determined by the network, i.e

        - takes as input active powers `P` of all non-slack buses, reactive
          powers of :class:`.ElectricalPQBus` and voltage amplitudes of
          :class:`.ElectricalPVBus`; all these values have to be placed by the
          user at the right place in the N-long vectors, `P`, `Q`, and,
          respectively, `V`, passed to this method

        - outputs active power of slack bus, reactive powers of
          :class:`.ElectricalPVBus`, voltage amplitudes of
          :class:`.ElectricalPQBus`, and voltage angles of all buses; all these
          values are placed by this method at the right place in the N-long
          vectors `P`, `Q`, `V`, and, respectively, Th, passed to this method.


        :param P: N-long vector of bus active powers, where N is the number of
            buses including slack.
        :type P: 1-dimensional numpy array of float
        :param Q: N-long vector of bus reactive powers, where N is the number of
            buses including slack.
        :type Q: 1-dimensional numpy array of float
        :param V: N-long vector of bus voltage amplitudes, where N is the number
            of buses including slack.
        :type V: 1-dimensional numpy array of float
        :param Th: N-long vector of bus voltage angles, where N is the number
            of buses including slack.
        :type Th: 1-dimensional numpy array of float
        :param scaled: specifies whether electrical input values are scaled
            or not
        :type scaled: boolean
        """
        # check input arguments and save them to internal variables _P, _Q,
        # and _V
        self._read_calculate_args(P, Q, V, Th, scaled)
        # initialize voltage amplitudes of PQ buses to 1.0
        self._V[self._is_PQ] = 1.0
        # initialize voltage angles of all buses to 0.0
        self._Th = np.zeros([self._nBu])

        self._nIter = 0
        while (self._residual_metric > self._residual_tolerance):
            # all bus voltage amplitude products
            V_1X = np.array([self._V])
            # 2-D array with 1 row containing vector V
            _matVV = V_1X.transpose() * V_1X

            # all bus voltage angle differences and their sin and cos values
            Th_1X = np.array([self._Th])
            # 2-D array with 1 row containing vector Th
            _matTh = Th_1X.transpose() - Th_1X
            _cos_matTh = np.cos(_matTh)
            _sin_matTh = np.sin(_matTh)

            # pre-compute with real part and imaginary part of admittance matrix
            _G_cos_matTh = self._G * _cos_matTh
            _G_sin_matTh = self._G * _sin_matTh
            _B_cos_matTh = self._B * _cos_matTh
            _B_sin_matTh = self._B * _sin_matTh

            # bus active powers computed from voltage amplitudes and phases
            P_calc = np.sum(_matVV * (_G_cos_matTh + _B_sin_matTh), axis=1)

            # bus reactive powers computed from voltage amplitudes and phases
            Q_calc = np.sum(_matVV * (_G_sin_matTh - _B_cos_matTh), axis=1)

            # residual errors on active and reactive powers
            _dPaux = self._P - P_calc
            _dQaux = self._Q - Q_calc

            # select residual error of all bus active powers except slack
            _dP = _dPaux[1:]
            # select residual error of PQ bus reactive powers
            _dQ = _dQaux[self._is_PQ]
            # concatenate residuals
            MM = np.concatenate([_dP, _dQ])

            self._residual_metric = max(abs(MM))

            # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

            # JACOBIAN


            # H part of the Jacobian Matrix

            _HOrig = _matVV * (_G_sin_matTh - _B_cos_matTh)

            _auxHorig = np.sum(-_HOrig, axis=1) - self._V ** 2 * np.diagonal(
                self._B)

            np.fill_diagonal(_HOrig, _auxHorig)

            _auxPosPQ = np.array(np.where(self._is_PQ == True))

            _H = _HOrig[1:len(_HOrig), 1:len(_HOrig)]



            # M part of the Jacobian Matrix

            _MOrig = _matVV * (-_G_cos_matTh - _B_sin_matTh)

            _auxMorig = np.sum(-_MOrig, axis=1) - self._V ** 2 * np.diagonal(
                self._G)

            np.fill_diagonal(_MOrig, _auxMorig)

            _M = _MOrig[_auxPosPQ[0, :], 1:len(_MOrig)]



            # N part of the Jacobian Matrix

            _NOrig = (V_1X.transpose() * (self._ones_vector)) * (
            _G_cos_matTh + _B_sin_matTh)

            _auxNorig = (
                ((self._ones_vector).transpose() * self._V) * (
                _G_cos_matTh + _B_sin_matTh))
            _auxNorig = np.sum(_auxNorig, axis=1)
            _auxNorig = _auxNorig + self._V * np.diagonal(self._G)

            np.fill_diagonal(_NOrig, _auxNorig)

            _N = _NOrig[1:len(_NOrig), _auxPosPQ[0, :]]


            # L part of the Jacobian Matrix

            _LOrig = (V_1X.transpose() * (self._ones_vector)) * (
            _G_sin_matTh - _B_cos_matTh)

            _auxLorig = (
                (self._ones_vector.transpose() * self._V) * (
                _G_sin_matTh - _B_cos_matTh))
            _auxLorig = np.sum(_auxLorig, axis=1)
            _auxLorig = _auxLorig - self._V * np.diagonal(self._B)

            np.fill_diagonal(_LOrig, _auxLorig)

            _L = _LOrig[_auxPosPQ, _auxPosPQ.transpose()]

            # Jacobian

            jacobian = np.vstack((np.hstack((_H, _N)), np.hstack((_M, _L))))

            # JacobianOrig = np.vstack(
            #     (np.hstack((_HOrig, _NOrig)), np.hstack((_MOrig, _LOrig))))

            # Compute changes from inverse Jacobian

            K = inv(jacobian).dot(MM)

            # Update Theta and V values

            # Extract dTH from K, dTH are voltage angle changes for all buses
            # except slack
            dTH = K[0:self._nBu - 1]
            # Extract dV from K, dV are voltage amplitude changes for all PV
            # buses
            dV = K[self._nBu - 1:]

            # Update Theta for all buses except slack
            self._Th[1:self._nBu] = self._Th[1:self._nBu] + dTH

            # Update V for all PV buses
            self._V[_auxPosPQ] = self._V[_auxPosPQ] + dV

            self._nIter += 1
            # print self._nIter
        # end of iteration loop

        # Compute final active and reactive powers for all buses
        p_calc = np.sum(_matVV * (_G_cos_matTh + _B_sin_matTh), axis=1)
        q_calc = np.sum(_matVV * (_G_sin_matTh - _B_cos_matTh), axis=1)

        # Update active power for slack
        self._P[0] = p_calc[0]
        # Update reactive power for slack and all PV buses
        self._Q[~self._is_PQ] = q_calc[~self._is_PQ]

        if not scaled:
            self._P *= self.s_base
            self._Q *= self.s_base
            self._V *= self.v_base

        return [self._P, self._Q, self._V, self._Th]
