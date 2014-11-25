import warnings

import numpy as np
from scipy.sparse import lil_matrix

from gridsim.decorators import accepts
from gridsim.unit import units
from gridsim.core import AbstractSimulationModule

from .core import AbstractElectricalElement, ElectricalBus, \
    ElectricalNetworkBranch, AbstractElectricalCPSElement
from .loadflow import AbstractElectricalLoadFlowCalculator
from .network import AbstractElectricalTwoPort, ElectricalTransmissionLine, \
    ElectricalGenTransformer, ElectricalSlackBus


class _BusElectricalValues(object):
    pass


class _BranchElectricalValues(object):
    pass


class ElectricalSimulator(AbstractSimulationModule):

    @accepts((1, AbstractElectricalLoadFlowCalculator))
    def __init__(self, calculator=None):
        """

        :param calculator: The load flow calculator used by the simulator
        :type calculator: AbstractElectricalLoadFlowCalculator
        """
        super(ElectricalSimulator, self).__init__()

        self._buses = []
        self._busDict = {}
        self._branches = []
        self._branchDict = {}
        self._cps_elements = []
        self._cps_elementDict = {}
        self._cps_elementBusMap = {}
        self._buses.append(None)
        self.add(ElectricalSlackBus("Slack Bus"))
        # TODO: allow to change the slack bus position
        self._hasChanges = False

        # matrix representing aggregation of CPS elements into buses
        self._mat_A = None
        # vector if CPS elements active power
        self._Pe = None

        # load flow
        # ----------
        self._load_flow_calculator = calculator

        # network
        self.s_base = 1.0
        self.v_base = 1.0
        self._is_PV = None
        self._mat_Y = None
        self._b = None

        # bus electrical values
        self._bu = _BusElectricalValues()

        # branches electrical values
        self._br = _BranchElectricalValues()


    @property
    def load_flow_calculator(self):
        return self._load_flow_calculator

    @load_flow_calculator.setter
    def load_flow_calculator(self, new_calculator):
        self._load_flow_calculator = new_calculator

    @accepts((1, AbstractElectricalElement))
    def add(self, element):
        if isinstance(element, ElectricalSlackBus):
            if self._buses[0] is None:
                self._buses[0] = element
                element.id = 0
                self._busDict[element.friendly_name] = element
            else:
                raise RuntimeError(
                    'Only one slack bus can be added to the simulator.')

        elif isinstance(element, ElectricalBus):
            if element.friendly_name is 'Slack Bus':
                warnings.warn(
                    'Slack Bus is an invalid name for a non-slack bus.')
            elif element.friendly_name in self._busDict.keys():
                raise RuntimeError(
                    'Duplicate Bus friendly name, must be unique.')
            element.id = len(self._buses)
            self._buses.append(element)
            self._busDict[element.friendly_name] = element

        elif isinstance(element, ElectricalNetworkBranch):
            if element.friendly_name in self._branchDict.keys():
                raise RuntimeError(
                    'Duplicate branch friendly name, must be unique.')
            elif element.from_bus_id is None or element.from_bus_id > len(
                    self._buses):
                raise RuntimeError('Invalid "from bus ID".')
            elif element.to_bus_id is None or element.to_bus_id > len(
                    self._buses):
                raise RuntimeError('Invalid "to bus ID".')
            element.id = len(self._branches)
            self._branches.append(element)
            self._branchDict[element.friendly_name] = element

        elif isinstance(element, AbstractElectricalCPSElement):
            if element.friendly_name in self._cps_elementDict.keys():
                raise RuntimeError(
                    'Duplicate electrical CPS element friendly name, '
                    'must be unique.')
            element.id = len(self._cps_elements)
            self._cps_elements.append(element)
            self._cps_elementDict[element.friendly_name] = element

        else:
            # TODO: also add these elements to appropriate list,
            # TODO: e.g. self.elements[element.__class__.__name__]
            pass
        self._hasChanges = True
        return element

    @accepts((1, (int, str)))
    def bus(self, id_or_friendly_name):
        if isinstance(id_or_friendly_name, int):
            if len(self._buses) > id_or_friendly_name:
                return self._buses[id_or_friendly_name]
            else:
                raise IndexError('Invalid index.')
        elif isinstance(id_or_friendly_name, str):
            if id_or_friendly_name in self._busDict.keys():
                return self._busDict[id_or_friendly_name]
            else:
                raise KeyError('Invalid key.')

    @accepts((1, (int, str)))
    def branch(self, id_or_friendly_name):
        if isinstance(id_or_friendly_name, int):
            if len(self._branches) > id_or_friendly_name:
                return self._branches[id_or_friendly_name]
            else:
                raise IndexError('Invalid index.')
        elif isinstance(id_or_friendly_name, str):
            if id_or_friendly_name in self._branchDict.keys():
                return self._branchDict[id_or_friendly_name]
            else:
                raise KeyError('Invalid key.')

    @accepts((1, (int, str)))
    def cps_element(self, id_or_friendly_name):
        if isinstance(id_or_friendly_name, int):
            if len(self._cps_elements) > id_or_friendly_name:
                return self._cps_elements[id_or_friendly_name]
            else:
                raise IndexError('Invalid index.')
        elif isinstance(id_or_friendly_name, str):
            if id_or_friendly_name in self._cps_elementDict.keys():
                return self._cps_elementDict[id_or_friendly_name]
            else:
                raise KeyError('Invalid key.')

    @accepts((1, str),
             (4, AbstractElectricalTwoPort))
    def connect(self, friendly_name, bus_a, bus_b, two_port):
        if not isinstance(bus_a, ElectricalBus):
            bus_a = self.bus(bus_a)
        if not isinstance(bus_b, ElectricalBus):
            bus_b = self.bus(bus_b)

        branch = self.add(
            ElectricalNetworkBranch(friendly_name, bus_a, bus_b, two_port))
        return branch

    @accepts((1, (int, str, ElectricalBus)),
             (2, (int, str, AbstractElectricalCPSElement)))
    def attach(self, bus, el):
        if not isinstance(bus, ElectricalBus):
            bus = self.bus(bus)
        if bus.type == ElectricalBus.Type.SLACK_BUS:
            raise RuntimeError('No element can be attached to slack bus')
        if not isinstance(el, AbstractElectricalCPSElement):
            el = self.element(el)
        if not el.friendly_name in self._cps_elementDict.keys():
            self.add(el)
        self._cps_elementBusMap[el.id] = bus.id
        self._hasChanges = True  # to recompute network description
        # element inherits bus position
        el.position = bus.position
        return None

    # SimulationModule implementation.
    def attribute_name(self):
        return 'electrical'

    def all_elements(self):
        elements = []
        elements.extend(self._buses)
        elements.extend(self._branches)
        elements.extend(self._cps_elements)
        return elements

    def reset(self):
        for element in self._buses:
            element.reset()
        for element in self._branches:
            element.reset()
        for element in self._cps_elements:
            element.reset()

    def _has_orphans(self):
        # TODO: check that all elements are attached to a bus and that all buses
        # TODO: are connected to at least one other bus through a line
        for element in self._cps_elements:
            if element.id not in self._cps_elementBusMap:
                return False
        return True

    def _prepare_matrices(self):

        # TODO verify unit

        L = len(self._cps_elements)  # number of elements
        M = len(self._branches)  # number of branches
        N = len(self._buses)  # number of buses

        # build matrix A to aggregate elements power to buses power,
        # as sparse matrix
        self._mat_A = lil_matrix((N, L))
        for i_el in range(0, L):
            self._mat_A[self._cps_elementBusMap[i_el], i_el] = 1.0
        # change sparse matrix representation
        self._mat_A = self._mat_A.tocsr()

        # build boolean vector specifying among the buses (except slack) which
        # one is a PV bus
        self._is_PV = np.empty(N, dtype=bool)
        for i_bus in range(0, len(self._buses)):
            self._is_PV[i_bus] = self._buses[i_bus] == ElectricalBus.Type.PV_BUS

        # build Mx2 table with from_bus and to_bus id of each branch
        self._b = np.empty((M, 2), dtype=int)
        for i_branch in range(0, len(self._branches)):
            self._b[i_branch, 0] = self._branches[i_branch].from_bus_id
            self._b[i_branch, 1] = self._branches[i_branch].to_bus_id

        # build table Yb of branch admittances
        self._Yb = np.zeros((M, 4), dtype=complex)*units.siemens
        # start with the off-diagonal element
        for i_branch in range(0, M):
            branch = self._branches[i_branch]
            if isinstance(branch._two_port, ElectricalTransmissionLine):
                tline = branch._two_port
                Y_line = 1. / (tline.R + 1j * tline.X)
                self._Yb[i_branch, 0] = Y_line + 1j * tline.B / 2
                self._Yb[i_branch, 1] = Y_line
                self._Yb[i_branch, 2] = Y_line + 1j * tline.B / 2
                self._Yb[i_branch, 3] = Y_line
            elif isinstance(branch._two_port, ElectricalGenTransformer):
                tap = branch._two_port
                Y_line = 1. / (tap.R + 1j * tap.X)
                self._Yb[i_branch, 0] = Y_line
                self._Yb[i_branch, 1] = Y_line / tap.k_factor
                self._Yb[i_branch, 2] = Y_line / (abs(tap.k_factor) ** 2)
                self._Yb[i_branch, 3] = Y_line / tap.k_factor.conjugate()

        # active power of electrical CPS elements
        self._Pe = np.zeros(L)*units.watt

        # bus electrical values
        self._bu.P = np.zeros(N)*units.watt
        self._bu.Q = np.zeros(N)*units.watt
        self._bu.V = np.zeros(N)*units.volt
        self._bu.Th = np.zeros(N)*units.degree

    def calculate(self, time, delta_time):
        for element in self._cps_elements:
            element.calculate(time, delta_time)

    def update(self, time, delta_time):

        if self._hasChanges and len(self._buses) > 1 \
                and len(self._branches) > 0:
            # TODO: raise warning if self._as_orphans():
            self._prepare_matrices()
            self.load_flow_calculator.update(self.s_base, self.v_base,
                                             self._is_PV, self._b, self._Yb)

            self._hasChanges = False

        for element in self._cps_elements:
            element.update(time, delta_time)

        if len(self._buses) > 1 and len(self._branches) > 0:
            # put element powers into corresponding array
            # ----------------------------------------------------
            scale_factor = 1 / delta_time
            for element in self._cps_elements:
                self._Pe[element.id] = scale_factor * element.delta_energy

            # compute vector of bus powers
            # -----------------------------
            self._bu.P = -self._mat_A.dot(self._Pe)

            # perform network computations
            #------------------------------
            self.load_flow_calculator.calculate(self._bu.P, self._bu.Q,
                                                self._bu.V, self._bu.Th, True)

            [self._br.Pij, self._br.Qij, self._br.Pji, self._br.Qji] = \
                self.load_flow_calculator.get_branch_power_flows(True)

            # put network computation results into network objects
            #-----------------------------------------------------
            for i_bus in range(1, len(self._buses)):
                self._buses[i_bus].Th = self._bu.Th[i_bus]
                self._buses[i_bus].P = self._bu.P[i_bus]*units.watt
                if self._is_PV[i_bus]:
                    self._buses[i_bus].Q = self._bu.Q[i_bus]*units.watt
                else:  # is PQ
                    self._buses[i_bus].V = self._bu.V[i_bus]*units.volt
            # slack
            self._buses[0].P = self._bu.P[0]*units.watt
            self._buses[0].Q = self._bu.Q[0]*units.watt
            self._buses[0].Th = 0*units.degree

            for i_branch in range(0, len(self._branches)):
                if not self._br.Pij is None:
                    self._branches[i_branch].Pij = self._br.Pij[i_branch]*units.watt
                else:
                    self._branches[i_branch].Pij = None
                if not self._br.Qij is None:
                    self._branches[i_branch].Qij = self._br.Qij[i_branch]*units.watt
                else:
                    self._branches[i_branch].Qij = None
                if not self._br.Pji is None:
                    self._branches[i_branch].Pji = self._br.Pji[i_branch]*units.watt
                else:
                    self._branches[i_branch].Pji = None
                if not self._br.Qji is None:
                    self._branches[i_branch].Qji = self._br.Qji[i_branch]*units.watt
                else:
                    self._branches[i_branch].Qji = None
