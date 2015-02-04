from gridsim.unit import units
from gridsim.core import AbstractSimulationElement, AbstractSimulationModule
from gridsim.simulation import Simulator
from gridsim.recorder import PlotRecorder
from gridsim.timeseries import TimeSeriesObject
from gridsim.iodata.input import CSVReader
from gridsim.iodata.output import FigureSaver


# Create own simulation element and module and
# register them within the simulator.
class MyObject(AbstractSimulationElement):

    def __init__(self, reader, file_name):
        super(MyObject, self).__init__(file_name)
        self._time_series = TimeSeriesObject(reader)
        self._time_series.load(file_name, time_converter=lambda t: t*units.day)

    def __getattr__(self, item):
        return getattr(self._time_series, item)

    def reset(self):
        pass

    def calculate(self, time, delta_time):
        pass

    def update(self, time, delta_time):
        self._time_series.set_time(time)

    def convert(self, item, converter):
        return self._time_series.convert(item, converter)


class MyModule(AbstractSimulationModule):
    def __init__(self):
        self._elements = []
        super(MyModule, self).__init__()

    def add(self, element):
        self._elements.append(element)
        return element

    def attribute_name(self):
        return 'my'

    def all_elements(self):
        return []

    def reset(self):
        pass

    def calculate(self, time, delta_time):
        pass

    def update(self, time, delta_time):
        for el in self._elements:
            el.update(time, delta_time)

Simulator.register_simulation_module(MyModule)


# Create a simulator, add an element and record the temperature signal using
# a recorder.
sim = Simulator()
obj = sim.my.add(MyObject(CSVReader(), './data/example_time_series.csv'))
obj.convert("temperature", lambda t: units(t, units.degC))

rec = PlotRecorder('temperature', units.month, units.kelvin)
sim.record(rec, obj)

print("Running simulation...")

sim.run(units.year, units.day)

print("Saving data...")

FigureSaver(rec, "Temperature").save('./output/timeseries2-example.png')