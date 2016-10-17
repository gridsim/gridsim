"""
.. moduleauthor:: Michael Clausen <clm@hevs.ch>
.. codeauthor:: Michael Clausen <clm@hevs.ch>

This module contains controlling elements. These can control any Python
attribute of an object based on the actual values of other attributes. The
classical example is a simple thermostat:

.. literalinclude:: ../../demo/thermostat.py
    :linenos:

This simulation outputs the following plots:

.. figure:: ../../demo/output/thermostat-fig1.png
            :align: center

.. figure:: ../../demo/output/thermostat-fig2.png
            :align: center

.. figure:: ../../demo/output/thermostat-fig3.png
            :align: center

"""
from .decorators import accepts, returns
from .util import Position
from .core import AbstractSimulationModule, AbstractSimulationElement
from .simulation import Simulator


class AbstractControllerElement(AbstractSimulationElement):

    @accepts((1, str), (2, Position))
    def __init__(self, friendly_name, position=Position()):
        """
        Base class of all element which can be part of a controller simulation.

        :param friendly_name: User friendly name to give to the element.
        :type friendly_name: str, unicode
        :param position: The position of the thermal element.
            Defaults to [0,0,0].
        :type position: :class:`Position`
        """
        super(AbstractControllerElement, self).__init__(friendly_name)
        self.position = position


class ControllerSimulator(AbstractSimulationModule):

    def __init__(self):
        """
        Simulation module for all controller simulation aspects.
        """
        super(ControllerSimulator, self).__init__()
        self._controllers = []

    @returns(str)
    def attribute_name(self):
        """
        AbstractSimulationModule implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationModule.attribute_name`.
        """
        return 'controller'

    def all_elements(self):
        """
        AbstractSimulationModule implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationModule.all_elements`.
        """
        return self._controllers

    def reset(self):
        """
        AbstractSimulationModule implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationModule.reset`.
        """
        for controller in self._controllers:
            controller.init()

    @accepts(((1, 2), (int, float)))
    def calculate(self, time, delta_time):
        """
        AbstractSimulationModule implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationModule.calculate`.
        """
        for controller in self._controllers:
            controller.calculate(time, delta_time)

    @accepts(((1, 2), (int, float)))
    def update(self, time, delta_time):
        """
        AbstractSimulationModule implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationModule.update`.
        """
        for controller in self._controllers:
            controller.update(time, delta_time)

    @accepts((1, AbstractControllerElement))
    def add(self, element):
        """
        Adds the control element to the controller simulation module.

        :param element: Element to add to the control simulator module.
        """
        element.id = len(self._controllers)
        self._controllers.append(element)
        return element


Simulator.register_simulation_module(ControllerSimulator)