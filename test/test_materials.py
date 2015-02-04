import unittest
from gridsim.util import Air, Aluminium, Material
from gridsim.unit import units


class TestMaterials(unittest.TestCase):

    def test_materials_creation(self):

        self.assertEqual(Air(), Air())

        self.assertNotEqual(Air(), Aluminium())

        self.assertEqual(Aluminium(), Aluminium())

        with self.assertRaises(SyntaxError):
            class MyNewAir(Air):  # raises the SyntaxError
                def __init__(self):
                    super(Air, self).__init__(1, 1000, 500)
            MyNewAir()

        with self.assertRaises(SyntaxError):
            Material(1, 1, 1)

    def test_materials_values(self):
        self.assertEqual(Air().thermal_capacity, 1005*units.heat_capacity)
        self.assertEqual(Air().weight, 1.2*units.mass_density)
        self.assertEqual(Air().thermal_conductivity,  0.02587*units.thermal_conductivity)


if __name__ == '__main__':
    unittest.main()
