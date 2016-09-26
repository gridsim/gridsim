from gridsim.decorators import accepts

class Aggregator(object):
    def __init__(self):
        super(Aggregator, self).__init__()
    def call(self,unitlist):
        raise NotImplementedError('Pure abstract method!')

class Callable(object):
    def __init__(self):
        super(Callable, self).__init__()
    def getValue(self,paramtype):
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
