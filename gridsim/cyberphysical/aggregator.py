"""
.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.cyberphysical.core import Aggregator

from gridsim.decorators import accepts, returns


class SumAggregator(Aggregator):
    def __init__(self, limit_min, limit_max, default=0):
        """
        __init__(self)

        Sum Aggregator class. This takes all the value and make a simple sum over them and return
        the result.
        """
        super(SumAggregator, self).__init__(limit_min, limit_max, default)

    def call(self, data):
        """
        call(self,data)

        Aggregate the data with a sum and return the result

        :param data: list of data to aggregate, in this case it's a sum
        :return: the sum of the given list value
        """
        res = 0
        for u in data:
            try:
                res += int(u)
            except TypeError:
                raise Exception('Cannot aggregate data - TypeError on int conversion')

        if res < self.limit_min:
            if self.default is not 0:
                res = self.default
            else:
                res = self.limit_min
        elif res > self.limit_max:
            if self.default is not 0:
                res = self.default
            else:
                res = self.limit_max

        return res


class MeanAggregator(Aggregator):
    def __init__(self, limit_min, limit_max, default=0):
        """
        __init__(self,limit_min,limit_max,default)

        Mean Aggregator class. This does the average value after calling the SumAggregator 'call' function
        """
        super(MeanAggregator, self).__init__(limit_min, limit_max, default)

        self._sum_aggregator = SumAggregator(limit_min, limit_max, default)

    @accepts((1, list))
    @returns((int, float))
    def call(self, data):
        # calculate the average value of the data list passed in parameter
        return self._sum_aggregator.call(data) / len(data)
