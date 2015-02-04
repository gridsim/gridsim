import unittest

from gridsim.unit import units
from gridsim.recorder import PlotRecorder


class TestRecorder(unittest.TestCase):

    def test_plot_recorder(self):

        recorder = PlotRecorder('power', units.minute, units.watt)

        recorder.on_simulation_reset(['foo', 'bar'])

        delta_time = units.value(1*units.minute, units.second)
        recorder.on_simulation_step(delta_time)
        recorder.on_observed_value('foo', delta_time, 14.2*units.watt)
        recorder.on_observed_value('bar', delta_time, 12*units.watt)

        delta_time = units.value(2*units.minute, units.second)
        recorder.on_simulation_step(delta_time)
        recorder.on_observed_value('foo', delta_time, 12*units.watt)
        recorder.on_observed_value('bar', delta_time, 12.1*units.watt)

        delta_time = units.value(3*units.minute, units.second)
        recorder.on_simulation_step(delta_time)
        recorder.on_observed_value('foo', delta_time, 16.1*units.watt)
        recorder.on_observed_value('bar', delta_time, 14.2*units.watt)

        delta_time = units.value(4*units.minute, units.second)
        recorder.on_simulation_step(delta_time)
        recorder.on_observed_value('foo', delta_time, 18.4*units.watt)
        recorder.on_observed_value('bar', delta_time, 9*units.watt)

        self.assertEqual(recorder.x_unit(), 'minute')
        self.assertEqual(recorder.x_values(), [1.0, 2.0, 3.0, 4.0])
        self.assertDictEqual(recorder.y_values(),
                             {'bar': [12, 12.1, 14.2, 9],
                              'foo': [14.2, 12, 16.1, 18.4]})
        self.assertEqual(recorder.y_unit(), 'watt')

if __name__ == '__main__':
    unittest.main()
