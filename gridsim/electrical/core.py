"""
.. moduleauthor:: Gilbert Maitre <gilbert.maitre@hevs.ch>

"""
from enum import Enum

from gridsim.decorators import accepts
from gridsim.core import AbstractSimulationElement
from gridsim.unit import units
from gridsim.util import Position


class AbstractElectricalElement(AbstractSimulationElement):

    @accepts((1, str))
    def __init__(self, friendly_name):
        """
        __init__(self, friendly_name)

        This class is the base for all elements that can take place in the
        electrical simulator. It is based on the general
        :class:`gridsim.core.AbstractSimulationElement`. At
        initialization the user has to give the element ``friendly_name``.

        :param friendly_name: Friendly name for the element.
            Should be unique within the simulation module.
        :type friendly_name: str

        """
        super(AbstractElectricalElement, self).__init__(friendly_name)


class ElectricalBus(AbstractElectricalElement):

    class Type(Enum):
        SLACK_BUS = 0
        """
        Type for slack (or swing) bus, i.e. the bus insuring that produced
        power is balanced to consumed power. Since it is unique, there is no
        input parameter for the slack bus.
        """
        PV_BUS = 1
        """
        Type for bus of type PV, i.e. bus where active power (P) and voltage
        amplitude (V) are given by the element(s) (generator) attached to the
        bus. Reactive power (Q) and voltage angle (Th) are then fixed by the
        network.
        """
        PQ_BUS = 2
        """
        Type for bus of type PQ, i.e. bus where active power (P) and
        reactive power (Q) are given by the element(s) (load) attached to the
        bus. Voltage amplitude (V) and voltage angle (Th) are then fixed by the
        network.
        """

    @accepts((1, str), (2, Type), (3, Position))
    def __init__(self, friendly_name, bus_type, position=Position()):
        """
        __init__(self, friendly_name, bus_type, position=Position())

        This class is the base for all type of buses (i.e. nodes) in the
        considered electrical network. It is based on the general
        :class:`AbstractElectricalElement` class. At initialization the user
        has to give the bus ``friendly_name``.

        If there is interest for the geographical ``position`` of the element,
        defined by the :class:`gridsim.util.Position` class. Apart from
        the methods provided by the superclass
        :class:`.AbstractElectricalElement`, this class provides the method
        ``position`` for getting the position property of the object.

        The chosen representation for bus electrical values is :
        active power (P), reactive power (Q), voltage amplitude
        (V), and voltage phase (Th). Their default values are None.

        :param friendly_name: Friendly name for the element.
            Should be unique within the simulation module.
        :type friendly_name: str

        :param bus_type: The type of the bus. Note that Slack Bus is
            automatically added to the simulation
        :type bus_type: :class:`ElectricalBus.Type`

        :param position: Bus geographical position.
            Defaults to Position default value.
        :type position: :class:`.Position`

        """
        super(ElectricalBus, self).__init__(friendly_name)

        self.type = bus_type
        """
        The type of the electrical bus (in Slack, PV, PQ)
        """

        self.position = position
        """
        The bus geographical position.
        """
        self.P = None
        """
        The bus active power.
        """
        self.Q = None
        """
        The bus reactive power.
        """
        self.V = None
        """
        The bus voltage amplitude.
        """
        self.Th = None
        """
        The bus voltage angle.
        """

    def reset(self):
        """
        reset(self)

        Reset bus electrical values to their default values: None
        """
        self.P = None
        self.Q = None
        self.V = None
        self.Th = None


class AbstractElectricalTwoPort(AbstractElectricalElement):

    @accepts((1, str))
    @units.wraps(None, (None, None, units.ohm, units.ohm))
    def __init__(self, friendly_name, X, R=0*units.ohm):
        """
        __init__(self, friendly_name, X, R=0*units.ohm)

        This class is the base for all electrical elements that can be placed
        on a network branch, e.g. transmission lines, transformers,
        phase shifters,... It is based on the general
        :class:`.AbstractElectricalElement` class. At initialization the user
        has to give the two-port ``friendly_name``.

        :param friendly_name: Friendly name for the element.
            Should be unique within the simulation module.
        :type friendly_name: str

        :param X: reactance of the element
        :type X: ohm, see :mod:`gridsim.unit`

        :param R: resistance of the element
        :type R: ohm, see :mod:`gridsim.unit`

        """
        super(AbstractElectricalTwoPort, self).__init__(friendly_name, )

        if X <= 0:
            raise RuntimeError('Line reactance X cannot be negative or null')
        if R < 0:
            raise RuntimeError('Line resistance R can not be negative number')

        self.X = X
        """
        The reactance.
        """
        self.R = R
        """
        The resistance.
        """


class ElectricalNetworkBranch(AbstractElectricalElement):

    @accepts((1, str),
             ((2, 3), ElectricalBus),
             (4, AbstractElectricalTwoPort))
    def __init__(self, friendly_name, from_bus, to_bus, two_port):
        """
        __init__(self, friendly_name, from_bus, to_bus, two_port)

        Class for a branch of an electrical network, i.e. connection between two
        buses (or nodes). It is oriented from one bus to the other. It is
        based on the general :class:`AbstractElectricalElement` class. At
        initialization, in addition to the 'friendly_name', the bus it is
        starting from, and the bus it is going to, have to be given, together
        with the two-port, e.g. transmission line, transformer,... it is made
        of.

        The chosen representation for branch electrical values is: active power
        ``Pi`` and reactive power ``Qi`` flowing into the branch at branch start,
        and active power Po and reactive power ``Qo`` flowing out of the branch at
        branch end. Their default values are None.

        :param friendly_name: Friendly name for the branch.
            Should be unique within the simulation module,
            i.e. different for example from the friendly name of a bus
        :type friendly_name: str

        :param from_bus: Electrical bus from which branch is starting.
        :type from_bus: :class:`.ElectricalBus`

        :param to_bus: Electrical bus to which branch is going.
        :type to_bus: :class:`.ElectricalBus`

        :param two_port: Electrical two-port on the branch,
            e.g. transmission line, transformer, ...
        :type two_port: :class:`.AbstractElectricalTwoPort`
        """
        if from_bus.id is None:
            raise RuntimeError('From_bus bus has not been added to simulator.')
        if to_bus.id is None:
            raise RuntimeError('To_bus bus has not been added to simulator.')

        super(ElectricalNetworkBranch, self).__init__(friendly_name)
        self._from_bus_id = from_bus.id
        self._to_bus_id = to_bus.id
        self._two_port = two_port
        self.Pij = None
        """
        Active power flowing into the branch from the from-bus terminal.
        """
        self.Qij = None
        """
        Reactive power flowing into the branch from the from-bus terminal.
        """
        self.Pji = None
        """
        Active power flowing into the branch from the to-bus terminal.
        """
        self.Qji = None
        """
        Reactive power flowing into the branch from the to-bus terminal.
        """

    @property
    def from_bus_id(self):
        """
        from_bus_id(self)

        Gets the id of the bus the branch is starting from.

        :returns: id of the bus the branch is starting from.
        :rtype: int
        """
        return self._from_bus_id

    @property
    def to_bus_id(self):
        """
        to_bus_id(self)

        Gets the id of the bus the branch is going to.

        :returns: id of the bus the branch is going to.
        :rtype: int
        """
        return self._to_bus_id

    def reset(self):
        """
        reset(self)

        Reset branch electrical values to their default : None
        """
        self.Pij = None
        self.Qij = None
        self.Pji = None
        self.Qji = None


class AbstractElectricalCPSElement(AbstractElectricalElement):

    @accepts((1, str))
    def __init__(self, friendly_name):
        """
        __init__(self, friendly_name)

        CPS stands for "Consuming-Producing-Storing".

        This class is based on the :class:`AbstractElectricalElement` class.
        It has the same initialization parameters : ``friendly_name``.
        It differs from the superclass :class:`AbstractElectricalElement` in
        giving access to the property ``delta_energy``, which is the amount of
        energy consumed or stored (if positive), produced or un-stored (if
        negative) during a simulation step. The class also implements the
        methods :func:`gridsim.core.AbstractSimulationElement.reset`
        to set the ``delta_energy`` property to 0 and
        :func:`gridsim.core.AbstractSimulationElement.update` to update the
        ``delta_energy`` property to its current value.

        :param friendly_name: Friendly name for the element. Should be unique
            within the simulation module.
        :type friendly_name: str

        """
        super(AbstractElectricalCPSElement, self).__init__(friendly_name)
        self._delta_energy = 0
        self._internal_delta_energy = 0

    @property
    def delta_energy(self):
        """
        delta_energy(self)

        Gets the element consumed energy during last simulation step. Getting a
        negative value means that. the element has produced energy.

        :returns: energy consumed by element during last simulation step.
        :rtype: time, see :mod:`gridsim.unit`
        """
        return self._delta_energy

    @delta_energy.setter
    def delta_energy(self, value):
        self._delta_energy = value

    def reset(self):
        """
        reset(self)

        Resets the element to its initial state.
        """
        self._delta_energy = 0
        self._internal_delta_energy = 0

    def update(self, time, delta_time):
        """
        update(self, time, delta_time)

        Updates ``delta_energy`` property to ist current value.

        :param time: The actual time of the simulator.
        :type time: time, see :mod:`gridsim.unit`
        :param delta_time: The delta time for which the update has to be done.
        :type delta_time: time, see :mod:`gridsim.unit`
        """
        self._delta_energy = self._internal_delta_energy
