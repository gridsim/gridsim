"""
.. moduleauthor:: Gillian Basso <gillian.basso@hevs.ch>

.. codeauthor:: Gilbert Maitre <gilbert.maitre@hevs.ch>

"""

from gridsim.decorators import accepts
from gridsim.util import Position
from gridsim.unit import units
from .core import AbstractElectricalTwoPort, ElectricalBus


class ElectricalTransmissionLine(AbstractElectricalTwoPort):

    @units.wraps(None, (None, None, units.metre, units.ohm, units.ohm, units.siemens))
    def __init__(self, friendly_name, length, X, R=0, B=0):
        """
        __init__(self, friendly_name, length, X, R=0, B=0)

        Class for representing a transmission line in an electrical network.
        Its parameters are linked to the
        transmission line PI model represented graphically below::

                                  R              jX
                            +-----------+   +-----------+
            o--->---o-------|           |---|           |-------o--->---o
                    |       +-----------+   +-----------+       |
                    |                                           |
                  -----  jB/2                                 -----  jB/2
                  -----                                       -----
                    |                                           |
                    |                                           |
                   ---                                         ---

        At initialization, in addition to the line ``friendly_name``,
        the line length, the line reactance (``X``), line resistance (``R``) and
        line charging (B) have to be given. ``R`` and ``B`` default to zero.

        :param friendly_name: Friendly name for the line. Should be unique
            within the simulation module, i.e. different for example from the
            friendly name of a bus.
        :type friendly_name: str

        :param length: Line length.
        :type length: length, see :mod:`gridsim.unit`

        :param X: Line reactance.
        :type X: ohm, see :mod:`gridsim.unit`

        :param R: Line resistance.
        :type R: ohm, see :mod:`gridsim.unit`

        :param B: Line charging.
        :type B: siemens, see :mod:`gridsim.unit`
        """
        # super constructor needs units as it is a "public" function
        super(ElectricalTransmissionLine, self).__init__(friendly_name, X*units.ohm, R*units.ohm)

        if length <= 0:
            raise RuntimeError('Length has to be a strictly positive number')
        if B < 0:
            raise RuntimeError('Line charging B can not be negative number')

        self.length = length
        """
        The transmission line length.
        """
        self.B = B
        """
        The transmission line charging.
        """


class ElectricalGenTransformer(AbstractElectricalTwoPort):

    @accepts((1, str), (2, complex))
    @units.wraps(None, (None, None, None, units.ohm, units.ohm))
    def __init__(self, friendly_name, k_factor, X, R=0):
        """
        __init__(self, friendly_name, k_factor, X, R=0)

        Class for representing a transformer and/or a phase shifter in an
        electrical network. Its parameters are
        linked to the usual transformer graphical representation below::

                                                             1:K
                          R              jX                 -   -
                    +-----------+   +-----------+        /   / \   \\
            o--->---|           |---|           |-------|---|--|---|------->---o
                    +-----------+   +-----------+       \   \ /   /
                                                           -   -

        While the transformer changes the voltage amplitude, the phase shifter
        changes the voltage phase. Accepting a complex ``K_factor`` parameter,
        the :class:`.ElectricalGenTransformer` is a common representation for a
        transformer and a phase shifter.

        At initialization, in addition to the line ``friendly_name``, the
        ``K-factor``, the reactance (``X``), and the resistance (``R``) have to be
        given. ``R`` defaults to zero.

        :param friendly_name: Friendly name for the transformer or phase
            shifter. Should be unique within the simulation module, i.e.
            different for example from the friendly name of a bus
        :type friendly_name: str

        :param k_factor: Transformer or phase shifter K-factor.
        :type k_factor: complex

        :param X: Transformer or phase shifter reactance.
        :type X: ohm, see :mod:`gridsim.unit`

        :param R: Transformer or phase shifter resistance.
        :type R: ohm, see :mod:`gridsim.unit`

        """
        # super constructor needs units as it is a "public" function
        super(ElectricalGenTransformer, self).__init__(friendly_name, X*units.ohm, R*units.ohm)

        if k_factor == 0:
            raise RuntimeError(
                'Transformer or phase shifter K-factor can not be null')

        self.k_factor = k_factor
        """
        The transformer or phase shifter K-factor.
        """


class ElectricalSlackBus(ElectricalBus):

    def __init__(self, friendly_name, position=Position()):
        """
        __init__(self, friendly_name, position=Position())

        Convenience class to define a Slack Bus.

        .. seealso:: :class:`.ElectricalBus`

        :param friendly_name: Friendly name for the element.
            Should be unique within the simulation module.
        :type friendly_name: str

        :param position: Bus geographical position.
            Defaults to Position default value.
        :type position: :class:`.Position`
        """
        super(ElectricalSlackBus, self)\
            .__init__(friendly_name, ElectricalBus.Type.SLACK_BUS, position)


class ElectricalPVBus(ElectricalBus):

    def __init__(self, friendly_name, position=Position()):
        """
        __init__(self, friendly_name, position=Position())

        Convenience class to define a PV Bus.

        .. seealso:: :class:`.ElectricalBus`

        :param friendly_name: Friendly name for the element.
            Should be unique within the simulation module.
        :type friendly_name: str

        :param position: Bus geographical position.
            Defaults to Position default value.
        :type position: :class:`.Position`
        """
        super(ElectricalPVBus, self)\
            .__init__(friendly_name, ElectricalBus.Type.PV_BUS, position)


class ElectricalPQBus(ElectricalBus):

    def __init__(self, friendly_name, position=Position()):
        """
        __init__(self, friendly_name, position=Position())

        Convenience class to define a PQ Bus.

        .. seealso:: :class:`.ElectricalBus`

        :param friendly_name: Friendly name for the element.
            Should be unique within the simulation module.
        :type friendly_name: str

        :param position: Bus geographical position.
            Defaults to Position default value.
        :type position: :class:`.Position`
        """
        super(ElectricalPQBus, self)\
            .__init__(friendly_name, ElectricalBus.Type.PQ_BUS, position)