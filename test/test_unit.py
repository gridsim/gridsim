import unittest

from pint.unit import DimensionalityError

from gridsim.unit import units


class TestUnit(unittest.TestCase):

    def test_value(self):
        m = 3000*units.metre

        g = 10*units.gram
        kg = 0.01*units.kg

        self.assertEqual(units.value(g), 10)
        self.assertEqual(units.value(kg), 0.01)
        self.assertEqual(units.value(kg*m), 30.)

        self.assertEqual(units.value(g, units.decagram), 1.)
        self.assertEqual(units.value(m, units.Mm), 0.003)  # Megametre

    def test_unit(self):

        m = 165*units.metre
        km = 3.965*units.kilometre

        c = 1.2*units.candelas

        self.assertEqual(units.unit(m), "meter")
        self.assertEqual(units.unit(km), "kilometer")
        self.assertEqual(units.unit(c), "candela")
        self.assertEqual(units.unit(c*m), "candela * meter")
        self.assertEqual(units.unit(m*km), "kilometer * meter")
        self.assertEqual(units.unit("toto"), "")  # returns "" if not a unit
        self.assertEqual(units.unit(4), "")  # returns "" if not a unit

    def test_si(self):

        km = 56*units.kilometre

        kg = 0.12*units.kilogram

        kwh = 43.1*units.kilowatthour

        self.assertEqual(units.value(units.to_si(km)), 56000)
        self.assertEqual(units.value(units.to_si(kg)), 0.12)
        self.assertEqual(units.value(units.to_si(kg*km)), 6720)
        self.assertEqual(units.value(units.to_si(kwh)), 155160000)  # joule
        self.assertRaises(AttributeError, self._value_si, 7)
        self.assertRaises(AttributeError, self._value_si, "85.2")

    def _value_si(self, a):
        return units.value(units.to_si(a))

    def test_convert(self):

        m = 3000*units.metre
        km = 3*units.kilometre

        g = 10*units.gram
        kg = 0.01*units.kilogram

        self.assertEqual(km, m)
        self.assertEqual(kg, g)

        self.assertEqual(units.convert(m, units.kilometer), km)
        self.assertEqual(units.convert(m, "kilometer"), 3.*units.km)
        self.assertRaises(DimensionalityError, self._convert, m, g)

    def _convert(self, a, u):
        return units.convert(a, u)

    def test_dimension(self):

        s = 12*units.second

        j = 59.1*units.joule

        self.assertEqual(units.dimension(s), "[time]")
        self.assertEqual(units.dimension(j), "[length] ** 2 * [mass] / [time] ** 2")

    def test_raises(self):

        m = 3000*units.metre

        g = 10*units.gram

        self.assertRaises(DimensionalityError, self._add, g, m)

    def _add(self, a, b):
        return a+b

if __name__ == '__main__':
    unittest.main()
