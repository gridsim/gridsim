from gridsim.decorators import accepts, returns
from gridsim.core import AbstractSimulationModule

from .core import AbstractCyberPhysicalSystem

class CyberPhysicalModule(AbstractSimulationModule):
    def __init__(self):
        super(CyberPhysicalModule, self).__init__()

        self.lacps = []

    @accepts((1,AbstractCyberPhysicalSystem))
    def add(self, acps):
        acps.id = len(self.lacps)
        self.lacps.append(acps)
        return acps

    def attribute_name(self):
        return "cyberphysicalmodule"

    def reset(self):
        for a in self.lacps:
            a.reset()

    def calculate(self, time, delta_time):
        print('simulation time', time)
        for actor in self.lacps:
            actor.calculate(time, delta_time)

    def update(self, time, delta_time):
        for actor in self.lacps:
            actor.update(time, delta_time)