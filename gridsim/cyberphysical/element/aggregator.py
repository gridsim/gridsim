"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.cyberphysical.core import Aggregator

class SumAggregator(Aggregator):
    def __init__(self):

        """

        __init__(self)

        Sum Aggregator class. This takes all the value and make a simple sum over them and return
        the result.

        """
        super(SumAggregator, self).__init__()

    def call(self,datalist):
        """

        call(self,datalist)

        Aggregate the datalist with a sum and return the result

        :param datalist: list of data to aggregate, in this case it's a sum
        :return: the sum of the given list value
        """
        res = 0
        for u in datalist:
            try:
                res = res + int(u)
            except TypeError:
                return 0
        return res
