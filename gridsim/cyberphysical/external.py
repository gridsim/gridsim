from gridsim.decorators import accepts
from gridsim.core import AbstractSimulationElement

from gridsim.cyberphysical.core import Callable, ParamListener

class Actor(Callable, ParamListener):
    def __init__(self):
        super(Actor, self).__init__()

        self.writeparamtype = []
        self.readparamtype = []

    def reset(self):
        raise NotImplementedError('Pure abstract method!')
    def getListWriteParam(self):  # return the params asked for
        return self.writeparamtype
    def getListReadParam(self):
        return self.readparamtype

class AbstractCyberPhysicalSystem(AbstractSimulationElement):
    def __init__(self,friendly_name):
        super(AbstractCyberPhysicalSystem, self).__init__(friendly_name)

        self.actors = []
        self.writeparamlist = []
        self.readparamlist = []

    @accepts((1,Actor))
    def add(self, actor):

        rparamlist = actor.getListReadParam()
        wparamlist = actor.getListWriteParam()

        for w in self.writeparamlist:
            for a in wparamlist:
                if a == w.paramtype:
                    w.addCallable(actor)
        for r in self.readparamlist:
            for a in rparamlist:
                if a == r.paramtype:
                    r.addListener(actor)

        actor.id = len(self.actors)
        self.actors.append(actor)
        return actor

    def readParams(self):
        raise NotImplementedError('Pure abstract method!')
    def writeParams(self,paramtype,data):
        raise NotImplementedError('Pure abstract method!')
    def reset(self):
        for a in self.actors:
            a.reset()

    def calculate(self, time, delta_time):
        read = self.readParams() #give it in the right order
        if read != None:
            for r in self.readparamlist:
                r.pushReadParam(read.pop(0))
        for w in self.writeparamlist:#check for multiple write in one time
            self.writeParams(w.paramtype,w.getWriteParam())

    def update(self, time, delta_time):
        pass