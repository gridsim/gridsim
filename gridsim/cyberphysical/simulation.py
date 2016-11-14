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
        pass
    def cyberphysicalReadEnd(self):
        pass

    def cyberphysicalWriteBegin(self):
        pass
    def cyberphysicalWriteEnd(self):
        pass

    def cyberphysicalModuleEnd(self):
        pass

class CyberPhysicalModule(AbstractSimulationModule):
    def __init__(self):
        """
        __init__(self)

        CyberPhysicalModule registers AbstractCyberPhysicalSystem (Element) and call
        calculate and update when the simulation is running

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
        for cps in self.lacps:
            cps.reset()

    def calculate(self, time, delta_time):
        for l in self.listener:
            l.cyberphysicalReadBegin()
        for cps in self.lacps:
            cps.calculate(time, delta_time)
        for l in self.listener:
            l.cyberphysicalReadEnd()

    def update(self, time, delta_time):
        for l in self.listener:
            l.cyberphysicalWriteBegin()
        for cps in self.lacps:
            cps.update(time, delta_time)
        for l in self.listener:
            l.cyberphysicalWriteEnd()

    def end(self, time):
        for l in self.listener:
            l.cyberphysicalModuleEnd()

class MinimalCyberPhysicalModule(AbstractSimulationModule):

    def __init__(self):
        """
        __init__(self)

        MinimalCyberPhysicalModule module used with FileReaderRT to be able to get the next time
        in the file with the given time of the simulation
        """
        self.elements = []
        super(MinimalCyberPhysicalModule, self).__init__()

    @accepts((1,AbstractSimulationElement))
    def add(self, element):
        element.id = len(self.elements)
        self.elements.append(element)
        return element

    def attribute_name(self):
        return 'minimalcyberphysicalmodule'

    def reset(self):
        for element in self.elements:
            element.init()

    def calculate(self, time, delta_time):
        for element in self.elements:
            element.calculate(time, delta_time)

    def update(self, time, delta_time):
        for element in self.elements:
            element.update(time, delta_time)