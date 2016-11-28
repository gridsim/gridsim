"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.core import AbstractSimulationModule, AbstractSimulationElement
from .external import AbstractCyberPhysicalSystem

from gridsim.decorators import accepts, returns


class CyberPhysicalModuleListener(object):
    def __init__(self):
        """
        __init__(self)

        CyberPhysicalModuleListener is a listener interface, inform when the module start a
        read or a write at the beginning and when it's done.

        """
        # fixme
        # super(CyberPhysicalModuleListener, self).__init__()
        pass

    def cyberphysical_read_begin(self):
        """

        cyberphysical_read_begin(self)

        This function is called by the module when the Read begin
        """
        pass

    def cyberphysical_read_end(self):
        """

        cyberphysical_read_end(self)

        This function is called by the module when the Read end
        """
        pass

    def cyberphysical_write_begin(self):
        """

        cyberphysical_write_begin(self)

        This function is called by the module when the Write begin
        """
        pass

    def cyberphysical_write_end(self):
        """

        cyberphysical_write_end(self)

        This function is called by the module when the Write end
        """
        pass

    def cyberphysical_module_begin(self):
        """

        cyberphysical_module_begin(self)

        This function is called by the module when the simulation begin
        """
        pass

    def cyberphysical_module_end(self):
        """
        cyberphysical_module_end(self)

        This function is called by the module when the simulation end
        """
        pass


class CyberPhysicalModule(AbstractSimulationModule):
    def __init__(self):
        """
        __init__(self)

        CyberPhysicalModule registers AbstractCyberPhysicalSystem (Element) and call
        calculate and update when the simulation is running.
        It inform all the subscribers, when a Read and Write start and end.
        This is useful for log the data at the end of the cycle for ones.
        """
        super(CyberPhysicalModule, self).__init__()

        self.acps = []
        self.module_listener = []

    @accepts((1, AbstractCyberPhysicalSystem))
    @returns((AbstractCyberPhysicalSystem))
    def add_actor_listener(self, acps):
        """
        add_actor_listener(self, acps)

        Add a AbstractCyberPhysicalSystem to the module list

        :param acps: AbstractCyberPhysicalSystem to register the the module
        :return: acps with id
        """
        acps.id = len(self.acps)
        self.acps.append(acps)
        return acps

    @accepts((1, CyberPhysicalModuleListener))
    @returns((CyberPhysicalModuleListener))
    def add_module_listener(self, actor):
        """
        add_module_listener(self,actor)

        add an actor to be module listener, call the actor when the simulation start and stop
        a read or write action, do the same the when the simulation start and stop

        :param actor: actor to notify the status of the simulation
        :return: actor
        """
        self.module_listener.append(actor)
        return actor

    def attribute_name(self):
        """
        attribut_name(self)

        return the static name of the module (cyberphysicalmodule)

        :return: cyberphysicalmodule module name
        """
        return "cyberphysicalmodule"

    def reset(self):
        for l in self.module_listener:
            l.cyberphysical_module_begin()
        for cps in self.acps:
            cps.reset()

    def calculate(self, time, delta_time):
        # inform all the listener that a read begin
        for l in self.module_listener:
            l.cyberphysical_read_begin()
        # call calculate on all listeners (read)
        for cps in self.acps:
            cps.calculate(time, delta_time)
        # inform for the end of the read
        for l in self.module_listener:
            l.cyberphysical_read_end()

    def update(self, time, delta_time):
        # inform all the listener that a write begin
        for l in self.module_listener:
            l.cyberphysical_write_begin()
        # call update on all listeners (write)
        for cps in self.acps:
            cps.update(time, delta_time)
        # infor for the end of the write
        for l in self.module_listener:
            l.cyberphysical_write_end()

    def end(self, time):
        # inform all listeners for the end of the simulation
        for l in self.module_listener:
            l.cyberphysical_module_end()


class MinimalCyberPhysicalModule(AbstractSimulationModule):
    def __init__(self):
        """
        __init__(self)

        MinimalCyberPhysicalModule module used to get the update and calculate function from the simulation
        This is useful to synchronize an Actor with the current step (time) of the simulation
        This class call all the listener and inform them for a step of simulation which include a calculate and
        an update to perform.
        """
        self.elements = []
        super(MinimalCyberPhysicalModule, self).__init__()

    @accepts((1, AbstractSimulationElement))
    def add_element(self, element):
        # add the element to the list and insert an id
        element.id = len(self.elements)
        self.elements.append(element)
        return element

    def attribute_name(self):
        return 'minimalcyberphysicalmodule'

    def reset(self):
        # call every elements for the reset step
        for element in self.elements:
            element.init()

    def calculate(self, time, delta_time):
        # call every elements for the calculate step
        for element in self.elements:
            element.calculate(time, delta_time)

    def update(self, time, delta_time):
        # call every element for the update step
        for element in self.elements:
            element.update(time, delta_time)
