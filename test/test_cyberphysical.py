import unittest


from gridsim.cyberphysical.aggregator import SumAggregator

class TestCyberPhysical(unittest.TestCase):
    def test_sum_aggregator(self):

        sum = SumAggregator(-1000,1000,0)

        l = [10,20,30]
        res = sum.call(l)
        self.assertEqual(res, 60)

        l = [-1000,-1000,-1000]
        res = sum.call(l)
        self.assertEqual(res, -1000)

        l = [1000,1000,1000]
        res = sum.call(l)
        self.assertEqual(res, 1000)

        sum = SumAggregator(-1000, 1000, 100)

        l = [1000,1000,1000]
        res = sum.call(l)
        self.assertEqual(res, 100)

if __name__ == '__main__':
    unittest.main()
