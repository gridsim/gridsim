import unittest

from gridsim.unit import units


class TestUnit(unittest.TestCase):

    def test_unit(self):
        m1 = 4*units.metre
        m2 = 4*units.metre
        km = 3*units.kilometre


if __name__ == '__main__':
    unittest.main()
