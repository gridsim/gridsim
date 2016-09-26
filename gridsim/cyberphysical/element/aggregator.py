from gridsim.cyberphysical.core import Aggregator

class SumAggregator(Aggregator):
    def __init__(self):
        super(SumAggregator, self).__init__()

    def call(self,unitlist):
        res = 0
        for u in unitlist:
            res = res + int(u)

        return res
