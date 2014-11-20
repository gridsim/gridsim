"""
.. moduleauthor:: Gillian Basso (gillian.basso@hevs.ch)

These tests verify the Gridsim decorators.
"""

import warnings
import unittest

from gridsim.decorators import accepts, returns, deprecated


# TODO manage __debug__


class Animal(object):
    @accepts((1, str))
    def __init__(self, race):
        self.race = race

    @accepts()
    @returns(str)
    def race(self):
        return self.race

    @accepts()
    @returns()
    def walks(self):
        print("The " + self.race() + " walks")

    @accepts()
    @returns()
    def swims(self):
        print("The " + self.race + " tries to swim")

    @accepts()
    @returns()
    def do_nothing(self):
        print("...")

    @returns(bool)
    def compare(self, other):
        if isinstance(other, Animal):
            return self.race == other.race
        return False

    @accepts((1, str))
    @returns()
    def set_race(self, new_race):
        self.race = new_race

    @accepts((2, int), (3, float), (4, int))
    @returns(bool)
    def default_params_func(self, i1=0, f=2.0, i2=4):
        return i1 * f + i2 > 0


class Duck(Animal):
    @accepts((1, str))
    def __init__(self, race):
        super(Duck, self).__init__(race)

    @accepts()
    @returns(str)
    def race(self):
        return "duck"

    @accepts()
    @returns()
    def quacks(self):
        print("The duck quacks")

    @accepts()
    @returns()
    def swims(self):
        print("The duck swims")


class Human(Animal):
    @accepts((1, str), (2, int))
    def __init__(self, race, age=0):
        super(Human, self).__init__(race)
        self.age = age

    @accepts()
    @returns(str)
    def race(self):
        return "human"

    @accepts()
    @returns()
    def talks(self):
        print("The human talks")

    @accepts()
    @returns()
    def swims(self):
        print ("The human flows")


class Child(Human):
    @accepts()
    def __init__(self):
        super(Child, self).__init__("child")


class TestDecorators(unittest.TestCase):
    @deprecated
    def deprecated_func(self):
        return True

    def valid_func(self):
        return True

    @returns(float)
    def return_int_demand_float(self):
        return 4

    @returns(int)
    def return_int_demand_int(self):
        return 4

    @returns(Human)
    def return_human_demand_human(self):
        return Human("h", 12)

    @returns(Animal)
    def return_human_demand_animal(self):
        return Human("h", 15)

    @returns(Animal)
    def return_child_demand_animal(self):
        return Child()

    @returns(Duck)
    def return_animal_demand_duck(self):
        return Animal("a")

    @returns()
    def return_nothing(self):
        pass

    @accepts((1, (int, float)),
             (2, float),
             (3, Animal),
             (4, Duck),
             (5, Human))
    def verify_params(self, n, f, animal, duck, human):
        return True

    @accepts()
    def verify_no_params(self):
        return True

    def test_accepts_raises(self):

        a = Animal("animal")
        d = Duck("duck")
        h = Human("human", 42)
        c = Child()

        self.assertRaises(TypeError, self.verify_no_params, 1.2)

        self.assertRaises(TypeError, self.verify_params, (1,   2.2, a, a, a))
        self.assertRaises(TypeError, self.verify_params, 1.1)
        self.assertRaises(TypeError, self.verify_params, ('a', 2.2, a, d, h))
        self.assertRaises(TypeError, self.verify_params, (1.1, 2,   a, d, h))
        self.assertRaises(TypeError, self.verify_params, (1,   2.2, a, c, h))

    def test_accepts_valid(self):
        a = Animal("animal")
        d = Duck("duck")
        h = Human("human", 17)
        c = Child()

        self.assertTrue(self.verify_no_params())
        self.assertTrue(a.default_params_func())
        self.assertTrue(d.default_params_func())
        self.assertTrue(c.default_params_func())

        self.assertTrue(self.verify_params(1.1, 2.2, a, d, h))
        self.assertTrue(self.verify_params(1,   2.2, a, d, h))
        self.assertTrue(self.verify_params(1.1, 2.2, d, d, h))
        self.assertTrue(self.verify_params(1,   2.2, h, d, h))
        self.assertTrue(self.verify_params(1,   2.2, c, d, c))

    def test_returns_raises(self):
        with self.assertRaises(TypeError):
            self.return_int_demand_float()
            self.return_animal_demand_duck()

    def test_returns_valid(self):
        self.assertIsInstance(self.return_int_demand_int(),      int)
        self.assertIsInstance(self.return_human_demand_human(),  Human)
        self.assertIsInstance(self.return_human_demand_animal(), Animal)
        self.assertIsInstance(self.return_child_demand_animal(), Animal)

    def test_deprecated_raises(self):
        warnings.simplefilter('error', DeprecationWarning)
        with self.assertRaises(DeprecationWarning):
            self.deprecated_func()
        warnings.simplefilter('default', DeprecationWarning)


if __name__ == '__main__':
    unittest.main()
