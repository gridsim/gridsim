import unittest

from gridsim.unit import units


class TestUnit(unittest.TestCase):

    def test_unit(self):
        m = 4*units.metre
        km = 3*units.kilometre

        print m.to(units.meter)
        print km.to(units.meter)


if __name__ == '__main__':
    unittest.main()
