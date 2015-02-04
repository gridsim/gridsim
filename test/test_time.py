import unittest

from gridsim.decorators import accepts, returns
from gridsim.unit import units
from gridsim.core import AbstractSimulationModule, \
    AbstractSimulationElement
from gridsim.simulation import Simulator


class TimeTestElement(AbstractSimulationElement):
    def __init__(self, friendly_name):
        super(TimeTestElement, self).__init__(friendly_name)

        self.val = None
        self._val = None

        self.iter = 0

    def reset(self):
        self.val = 0
        self._val = 0

    def calculate(self, time, delta_time):
        self._val += delta_time

    def update(self, time, delta_time):
        self.val = self._val
        self.iter += 1


class TimeTestModule(AbstractSimulationModule):

    def __init__(self):
        self.elements = []
        super(TimeTestModule, self).__init__()

    @accepts((1, TimeTestElement))
    @returns(TimeTestElement)
    def add(self, element):
        element.id = len(self.elements)
        self.elements.append(element)
        return element

    def attribute_name(self):
        return 'time_test'

    def reset(self):
        for element in self.elements:
            element.reset()

    def calculate(self, time, delta_time):
        for element in self.elements:
            element.calculate(time, delta_time)

    def update(self, time, delta_time):
        for element in self.elements:
            element.update(time, delta_time)

Simulator.register_simulation_module(TimeTestModule)


class TestTime(unittest.TestCase):

    def test_simulation_time(self):

        total_time = 1*units.hour
        delta_time = 1*units.second

        sim = Simulator()
        el = sim.time_test.add(TimeTestElement('test'))
        sim.reset()
        sim.run(total_time, delta_time)

        self.assertEqual(el.val, units.value(total_time, units.second))
        self.assertEqual(el.iter, 3601)  # from 0 to 3601 included

if __name__ == '__main__':
    unittest.main()
