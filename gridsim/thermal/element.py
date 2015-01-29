from gridsim.decorators import accepts
from gridsim.util import Position
from gridsim.unit import units
from gridsim.thermal.core import ThermalProcess
from gridsim.timeseries import TimeSeries


class ConstantTemperatureProcess(ThermalProcess):

    @accepts((1, (str, unicode)),
             (3, Position))
    def __init__(self, friendly_name, temperature, position=Position()):
        """
        This is a special thermal process with an infinite thermal capacity
        which results that the temperature of the process is constant,
        independent how much energy is taken from or given to the process.

        :param friendly_name: Friendly name to give to the process.
        :type friendly_name: str, unicode
        :param temperature: The (constant) temperature in degrees celsius.
        :type temperature: temperature
        :param position: The position of the :class:`.ThermalProcess`.
        :type position: :class:`Position`
        """

        super(ConstantTemperatureProcess, self).__init__(
            friendly_name,
            float('inf')*units.heat_capacity, temperature,
            position=position)

    @accepts((1, (int, float)))
    def add_energy(self, delta_energy):
        """
        Does nothing at all for this type of :class:`.ThermalProcess`.
        """
        pass

    @accepts(((1, 2), (int, float)))
    def update(self, time, delta_time):
        """
        Does nothing at all for this type of :class:`.ThermalProcess`.
        """
        pass


class TimeSeriesThermalProcess(ThermalProcess):

    @accepts(((1, 3), str),
             (2, TimeSeries),
             (5, Position))
    def __init__(self, friendly_name, time_series, stream, time_converter=None,
                 temperature_calculator=lambda t: units.convert(t, units.kelvin),
                 position=Position()):
        """
        Thermal process that reads the temperature out of a time series object
        (CSV file). It has an infinite thermal capacity.

        .. warning::

            It is important that the given data contains the
            field 'temperature' or you map a field to the attribute
            'temperature' using the function :func:`.TimeSeriesObject.map_attribute()`.

        :param friendly_name: Friendly name to give to the process.
        :type friendly_name: str, unicode
        :type time_series: :class:`gridsim.timeseries.TimeSeries`
        :param stream: The stream
        :type stream: str or stream
        :param temperature_calculator:
        :param position: The position of the thermal process.
        :type position: :class:`Position`
        """
        super(TimeSeriesThermalProcess, self).\
            __init__(friendly_name,
                     float('inf')*units.heat_capacity, 0*units.kelvin,
                     1*units.kilogram,
                     position)

        self._time_series = time_series
        self._time_series.load(stream, time_converter=time_converter)

        self._temperature_calculator = temperature_calculator

        self._time_series.convert('temperature', self._temperature_calculator)

        self.calculate(0*units.second, 0*units.second)

    def __getattr__(self, item):
        # this function is not called when using thermalprocess.temperature
        # because its parent (ThermalProcess) already has a 'temperature'
        return units.value(getattr(self._time_series, item))

    def reset(self):
        """
        Sets the time to default (``0``).

        .. seealso:: :func:`gridsim.timeseries.TimeSeriesObject.set_time`
        """
        self._time_series.set_time()

    def calculate(self, time, delta_time):
        """
        Calculates the temperature of the element during the simulation step.

        .. seealso:: :func:`gridsim.timeseries.TimeSeriesObject.set_time`
        """
        self._time_series.set_time(time)
        # the parent (ThermalProcess) already has a 'temperature' in
        # its local params
        self.temperature = units.value(self._time_series.temperature)

    def update(self, time, delta_time):
        """
        Does nothing for this type of :class:`.ThermalProcess`.
        """
        pass
