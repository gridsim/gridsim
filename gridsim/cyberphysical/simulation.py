"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.core import AbstractSimulationModule, AbstractSimulationElement
from .external import AbstractCyberPhysicalSystem

from gridsim.decorators import accepts

class CyberPhysicalModuleListener(object):
    def __init__(self):
        """
        __init__(self)

        CyberPhysicalModuleListener is a listener interface, inform when the module start a
        read or a write at the beginning and when it's done.

        """
        #fixme
        #super(CyberPhysicalModuleListener, self).__init__()
        pass

    def cyberphysicalReadBegin(self):
        """

        cyberphysicalReadBegin(self)

        This function is called by the module when the Read begin
        """
        pass
    def cyberphysicalReadEnd(self):
        """

        cyberphysicalReadEnd(self)

        This function is called by the module when the Read end
        """
        pass

    def cyberphysicalWriteBegin(self):
        """

        cyberphysicalWriteBegin(self)

        This function is called by the module when the Write begin
        """
        pass

    def cyberphysicalWriteEnd(self):
        """

        cyberphysicalWriteEnd(self)

        This function is called by the module when the Write end
        """
        pass

    def cyberphysicalModuleBegin(self):
        """

        cyberphysicalModuleBegin(self)

        This function is called by the module when the simulation begin
        """
        pass

    def cyberphysicalModuleEnd(self):
        """

        cyberphysicalModuleEnd(self)

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

        self.lacps = []
        self.listener = []

    @accepts((1,AbstractCyberPhysicalSystem))
    def add(self, acps):
        """

        add(self, acps)

        Add a AbstractCyberPhysicalSystem to the module list

        :param acps: AbstractCyberPhysicalSystem to register the the module
        :return: acps with id
        """
        acps.id = len(self.lacps)
        self.lacps.append(acps)
        return acps

    @accepts((1, CyberPhysicalModuleListener))
    def addModuleListener(self, actor):

        self.listener.append(actor)

    def attribute_name(self):
        """

        attribut_name(self)

        return the static name of the module (cyberphysicalmodule)

        :return: cyberphysicalmodule module name
        """
        return "cyberphysicalmodule"

    def reset(self):
        for l in self.listener:
            l.cyberphysicalModuleBegin()
        for cps in self.lacps:
            cps.reset()

    def calculate(self, time, delta_time):
        #inform all the listener that a read begin
        for l in self.listener:
            l.cyberphysicalReadBegin()
        #call calculate on all listeners (read)
        for cps in self.lacps:
            cps.calculate(time, delta_time)
        #inform for the end of the read
        for l in self.listener:
            l.cyberphysicalReadEnd()

    def update(self, time, delta_time):
        #inform all the listener that a write begin
        for l in self.listener:
            l.cyberphysicalWriteBegin()
        #call update on all listeners (write)
        for cps in self.lacps:
            cps.update(time, delta_time)
        #infor for the end of the write
        for l in self.listener:
            l.cyberphysicalWriteEnd()

    def end(self, time):
        #inform all listeners for the end of the simulation
        for l in self.listener:
            l.cyberphysicalModuleEnd()

class MinimalCyberPhysicalModule(AbstractSimulationModule):

    def __init__(self):
        """
        __init__(self)

        MinimalCyberPhysicalModule module used  to get the update and calculate function from the simulation
        This is useful to synchronize an Actor with the current step (time) of the simulation
        This class call all the listener and inform them for a step of simulation which include a calculate and
        an update to perform.
        """
        self.elements = []
        super(MinimalCyberPhysicalModule, self).__init__()

    @accepts((1,AbstractSimulationElement))
    def add(self, element):
        #add the element to the list and insert an id
        element.id = len(self.elements)
        self.elements.append(element)
        return element

    def attribute_name(self):
        return 'minimalcyberphysicalmodule'

    def reset(self):
        #call every elements for the reset step
        for element in self.elements:
            element.init()

    def calculate(self, time, delta_time):
        #call every elements for the calculate step
        for element in self.elements:
            element.calculate(time, delta_time)

    def update(self, time, delta_time):
        #call every element for the update step
        for element in self.elements:
            element.update(time, delta_time)