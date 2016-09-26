from gridsim.decorators import accepts

from gridsim.core import AbstractSimulationElement

class Callable(object):
    def __init__(self):
        super(Callable, self).__init__()
    def getValue(self,paramtype):
        raise NotImplementedError('Pure abstract method!')

class Aggregator(object):
    def __init__(self):
        super(Aggregator, self).__init__()
    def call(self,unitlist):
        raise NotImplementedError('Pure abstract method!')

class WriteParam(object):
    def __init__(self, paramtype, aggregate):
        super(WriteParam, self).__init__()

        self._aggregator = aggregate
        self.paramtype = paramtype

        self._callable = []
        self.unitlist = [] #list for aggregation

    @accepts((1,Aggregator))
    def setAggregator(self,aggregator):
        self._aggregator = aggregator

    @accepts((1, Callable))
    def addCallable(self,callable):
        self._callable.append(callable)

    def getWriteParam(self):
        self.unitlist = [] # clear
        for c in self._callable:
            self.unitlist.append(c.getValue(self.paramtype))
        if self.aggregate == None:
            raise NotImplementedError('Aggregate function not defined!')
        else:
            return self.aggregate(self.unitlist)

    def aggregate(self, unitlist):
        return self._aggregator.call(unitlist)

    def reset(self):
        self.unitlist = []  # clear

class ParamListener(object):
    def __init__(self):
        super(ParamListener, self).__init__()

    def notifyReadParam(self,paramtype,data):
        raise NotImplementedError('Pure abstract method!')

class ReadParam(object):
    def __init__(self, paramtype):
        super(ReadParam, self).__init__()

        self._listener = []
        self.unit = None

        self.paramtype = paramtype

    @accepts((1, ParamListener))
    def addListener(self,listener):
        self._listener.append(listener)

    def pushReadParam(self,unit):
        self.unit = unit
        for l in self._listener:
            l.notifyReadParam(self.paramtype,self.unit)

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
        read = self.readParams()
        for r in self.readparamlist:
            r.pushReadParam(read.pop(0))
        for w in self.writeparamlist:
            self.writeParams(w.paramtype,w.getWriteParam())

    def update(self, time, delta_time):
        pass