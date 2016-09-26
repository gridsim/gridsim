from .core import AbstractCyberPhysicalSystem, WriteParam, ReadParam, Aggregator

class GridLabCyberPhysicalSystem(AbstractCyberPhysicalSystem):
    def __init__(self,friendly_name):
        super(GridLabCyberPhysicalSystem, self).__init__(friendly_name)

        self.rlist = None
        self.wlist = None

    def initialize(self,readparamlist, writeparamlist):
        self.rlist = readparamlist
        self.wlist = writeparamlist

        for r in self.rlist:
            self.readparamlist.append(ReadParam(r))
        for w in self.wlist:
            self.writeparamlist.append(WriteParam(w, SumAggregator()))

    def readParams(self):
        return [10,20]
    def writeParams(self,paramtype,data):
        print('writeparams ' + str(paramtype) + ' ' + str(data))

class SumAggregator(Aggregator):
    def __init__(self):
        super(SumAggregator, self).__init__()

    def call(self,unitlist):
        res = 0
        for u in unitlist:
            res = res + int(u)

        return res
