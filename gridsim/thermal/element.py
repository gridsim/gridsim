from gridsim.decorators import accepts
from gridsim.util import Position
from gridsim.unit import units
from gridsim.thermal.core import ThermalProcess
from gridsim.timeseries import TimeSeriesObject
from gridsim.iodata.input import Reader


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
        :param position: The position of the thermal process.
        :type position: :class:`Position`
        """

        super(ConstantTemperatureProcess, self).__init__(
            friendly_name,
            float('inf')*units.heat_capacity, temperature,
            position=position)

    def add_energy(self, delta_energy):
        """
        Does nothing at all for this type of thermal process.
        """
        pass

    def update(self, time, delta_time):
        """
        AbstractSimulationElement implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationElement.update`.
        """
        pass


class TimeSeriesThermalProcess(ThermalProcess):

    @accepts(((1, 3), str),
             (2, Reader),
             (5, Position))
    def __init__(self, friendly_name, reader, stream, time_converter=None,
                 temperature_calculator=lambda t: t*units.kelvin,
                 position=Position()):
        """
        Thermal process that reads the temperature out of a time series object
        (CSV file). It has an infinite thermal capacity.

        .. warning::

            It is important that the given data file (CSV file) contains the
            field 'temperature' or you map a field to the attribute
            'temperature' using the function :func:`TimeSeriesObject.map()`.

        :param friendly_name: Friendly name to give to the process.
        :type friendly_name: str, unicode
        :type reader: Reader
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

        self._time_series = TimeSeriesObject(reader)
        self._time_series.load(stream, time_converter=time_converter)

        self._temperature_calculator = temperature_calculator

    def __getattr__(self, item):
        return self._temperature_calculator(getattr(self._time_series, item))

    def reset(self):
        """
        AbstractSimulationElement implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationElement.reset`.
        """
        self._time_series.set_time()

    def calculate(self, time, delta_time):
        """
        AbstractSimulationElement implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationElement.calculate`.
        """
        self._time_series.set_time(time)

    def update(self, time, delta_time):
        """
        AbstractSimulationElement implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationElement.update`.
        """
        pass
