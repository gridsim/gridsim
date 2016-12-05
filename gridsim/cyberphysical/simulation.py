"""
.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.core import AbstractSimulationModule, AbstractSimulationElement
from .element import AbstractCyberPhysicalSystem

from gridsim.decorators import accepts, returns

from multiprocessing.dummy import Pool as ThreadPool


class CyberPhysicalModuleListener:
    def __init__(self):
        """
        __init__(self)

        This Listener is informed when the module start an action (read, write) or at the initialisation
        (:func:`CyberPhysicalModule.reset()`) or the end (:func:`CyberPhysicalModule.end()`) of a step.

        .. warning:: This interface does not extend ``object`` class. As its implementation should implements
                another class (e.g. :class:`ParamListener`), a
                `diamond problem <https://en.wikipedia.org/wiki/Multiple_inheritance#The_diamond_problem>`_
                could arise.
        """
        pass

    def cyberphysical_read_begin(self):
        """
        cyberphysical_read_begin(self)

        Called by the module when the Read begin.
        """
        pass

    def cyberphysical_read_end(self):
        """
        cyberphysical_read_end(self)

        Called by the module when the Read end.
        """
        pass

    def cyberphysical_write_begin(self):
        """
        cyberphysical_write_begin(self)

        Called by the module when the Write begin.
        """
        pass

    def cyberphysical_write_end(self):
        """

        cyberphysical_write_end(self)

        Called by the module when the Write end.
        """
        pass

    def cyberphysical_module_begin(self):
        """
        cyberphysical_module_begin(self)

        Called by the module when the simulation begin.
        """
        pass

    def cyberphysical_module_end(self):
        """
        cyberphysical_module_end(self)

        Called by the module when the simulation end.
        """
        pass


class CyberPhysicalModule(AbstractSimulationModule):
    def __init__(self):
        """
        __init__(self)

        CyberPhysicalModule registers :class:`AbstractCyberPhysicalSystem` (which are
        :class:`gridsim.core.AbstractSimulationElement) and calls
        :func:`gridsim.core.AbstractSimulationElement.calculate` and
        :func:`gridsim.core.AbstractSimulationElement.update` when the simulation is running.
        It informs all the subscribers, when a Read and Write start and end.
        This allows easy logging at the end of a cycle.
        """
        super(CyberPhysicalModule, self).__init__()

        self._acps = []
        self._module_listener = []

        self._pool = ThreadPool(2)

    @accepts((1, AbstractCyberPhysicalSystem))
    @returns(AbstractCyberPhysicalSystem)
    def add_actor_listener(self, acps):
        """
        add_actor_listener(self, acps)

        Adds an :class:`gridsim.core.AbstractCyberPhysicalSystem` to the module list.

        :param acps: :class:`gridsim.cyberphysical.external.AbstractCyberPhysicalSystem` to register the the module
        :return: the :class:`gridsim.cyberphysical.external.AbstractCyberPhysicalSystem`.
        """
        acps.id = len(self._acps)
        self._acps.append(acps)
        return acps

    @accepts((1, CyberPhysicalModuleListener))
    @returns(CyberPhysicalModuleListener)
    def add_module_listener(self, listener):
        """
        add_module_listener(self,actor)

        Adds a :class:`CyberPhysicalModuleListener` to the module , calls the listener when the simulation starts,
        stops, or do an action (read or write).

        :param listener: :class:`CyberPhysicalModuleListener` to notify the status of the simulation
        :return: the :class:`CyberPhysicalModuleListener`
        """
        self._module_listener.append(listener)
        return listener

    def attribute_name(self):
        """
        attribut_name(self)

        Returns the name of this module.
        This name is used to access to this electrical simulator from the
        :class:`.Simulator`::

            # Create the simulation.
            sim = Simulator()
            the_sim = sim.cyberphysical

        :return: 'cyberphysical'
        :rtype: str
        """
        return "cyberphysical"

    def reset(self):
        for l in self._module_listener:
            l.cyberphysical_module_begin()
        for cps in self._acps:
            cps.reset()

    def calculate(self, time, delta_time):
        # inform all the listener that a read begin
        for l in self._module_listener:
            l.cyberphysical_read_begin()
        # call calculate on all listeners (read)
        for cps in self._acps:
            cps.calculate(time, delta_time)
        # inform for the end of the read
        for l in self._module_listener:
            l.cyberphysical_read_end()

    def update(self, time, delta_time):
        # inform all the listener that a write begin
        for l in self._module_listener:
            l.cyberphysical_write_begin()
        # call update on all listeners (write)
        for cps in self._acps:
            cps.update(time, delta_time)

        #self._pool = ThreadPool(2)
        #self._pool.map(AbstractCyberPhysicalSystem.regulation,self._acps)

        for cps in self._acps:
            cps.regulation()

        print 'test'

        #self._pool.close()
        #self._pool.join()

        # inform for the end of the write
        for l in self._module_listener:
            l.cyberphysical_write_end()

    def end(self, time):
        # inform all listeners for the end of the simulation
        for l in self._module_listener:
            l.cyberphysical_module_end()


class MinimalCyberPhysicalModule(AbstractSimulationModule):
    def __init__(self):
        """
        __init__(self)

        This module is used to get the update and calculate function from the simulation.
        This is useful to synchronize an :class:`gridsim.cyberphysical.external.Actor` with the current step (time) of
        the simulation. This class calls all the listeners and informs them for a step of simulation which include when
        a :func:`gridsim.core.AbstractSimulationElement.calculate` and
        :func:`gridsim.core.AbstractSimulationElement.update` functions are called.
        """
        self._elements = []
        super(MinimalCyberPhysicalModule, self).__init__()

    @accepts((1, AbstractSimulationElement))
    def add_element(self, element):
        # add the element to the list and insert an id
        element.id = len(self._elements)
        self._elements.append(element)
        return element

    def attribute_name(self):
        return 'minimalcyberphysical'

    def reset(self):
        for element in self._elements:
            element.reset()

    def calculate(self, time, delta_time):
        # call every elements for the calculate step
        for element in self._elements:
            element.calculate(time, delta_time)

    def update(self, time, delta_time):
        # call every element for the update step
        for element in self._elements:
            element.update(time, delta_time)
