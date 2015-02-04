"""
.. moduleauthor:: Gillian Basso <gillian.basso@hevs.ch>
.. codeauthor:: Michael Clausen <clm@hevs.ch>
.. codeauthor:: Gillian Basso <gillian.basso@hevs.ch>

The :mod:`gridsim.timeseries` module allows to import time series based on data
:class:`.Reader` as attributes.

The data are translated into attributes of the :class:`TimeSeries` by calling
the :func:`TimeSeries.load` method on a TimeSeriesObject or any subclass of it::

    obj = TimeSeries()
    obj.load('../../data/examples/example.csv')

This will call the :func:`gridsim.iodata.input.Reader.load` function and process
the data to simplify the access from the simulator.

It is important to have a ``time`` data or to identify the data representing the
time.

If the data contain a ``temperature`` data, it can be access with:

.. literalinclude:: ../../demo/timeseries.py
    :linenos:

This would give an output like this::

    20.0
    18.5

"""
import types
import warnings
from io import BufferedReader

from types import FunctionType

from .decorators import accepts
from .unit import units
from .iodata.input import Reader


class TimeSeries(object):

    @accepts((1, Reader))
    def __init__(self, reader):
        """
        __init__(self, reader)

        The time series objects allows to process data from :class:`.Reader`
        into a time series and allows to access these in a very simple way by
        providing them as attributes.

        *Example*:

        .. literalinclude:: ../../demo/timeseries2.py

        The result of the script:

        .. figure:: ../../demo/output/timeseries2-example.png
            :align: center
        """
        super(TimeSeries, self).__init__()

        self._reader = reader
        self._data = None
        self._index = 0
        self._time_key = 'time'

    def __getattr__(self, item):
        raise NotImplementedError('Pure abstract method!')

    @accepts(((1, 2), str), (3, bool))
    def map_attribute(self, name, mapped_name, is_time_key=False):
        """
        map_attribute(self, name, mapped_name, is_time_key=False)

        If the attribute name of the file does not match the target attribute
        name for the object, you can use this method to map the original name to
        a new attribute name.

        .. warning:: The old mapping will be removed.


        *Example*::

            obj.map('temp', 'temperature')

        The example will change the name of the attribute mapped to the data
        column from 'temp' to 'temperature'.

        .. warning:: the old value is delete from the :class:`TimeSeries`

        :param name: Original name of the attribute/column.
        :type name: str
        :param mapped_name: New name for the attribute.
        :type mapped_name: str
        :param is_time_key: should be True if the modified name is the time key.
        :type is_time_key: bool

        """
        if name not in self._data:
            raise AttributeError('No such attribute {0}'.format(name))
        if mapped_name in self._data:
            raise AttributeError(
                'Can not map attribute {0}, as it exists already.'.format(
                    mapped_name))

        if is_time_key:
            self._time_key = name

        if name is self._time_key:
            self._time_key = mapped_name

        self._data[mapped_name] = self._data.pop(name)


    @accepts((1, str), (2, FunctionType))
    def convert(self, item, converter):
        """
        convert(self, item, converter)

        Convert each element of the list mapped by ``item`` with the ``convert``
        function.

        :param item: the key of the list to convert
        :type item: str

        :param converter: the conversion function
        :type converter: function

        """
        self._data[item] = map(converter, self._data[item])

    @units.wraps(None, (None, units.second), strict=False)
    def set_time(self, time):
        """
        set_time(self, time=0)

        Changes the actual time on the object.

        :param time: the new time.
        :type time: float, int or time, see :mod:`gridsim.unit`
        """
        raise NotImplementedError('Pure abstract method!')

    @accepts((1, (str, BufferedReader)),
             (2, (None, types.MethodType)),
             (3, str))
    def load(self, stream, time_converter=None, time_key='time'):
        raise NotImplementedError('Pure abstract method!')


class TimeSeriesObject(TimeSeries):

    @accepts((1, Reader))
    def __init__(self, reader):
        """
        This class is the standard time series implementation with no assumption
        about data.

        This class has a :func:`TimeSeriesObject.compile_data` function to
        optimize the process but is still slow.
        """
        super(TimeSeriesObject, self).__init__(reader)

        self._computed_data = None

    @accepts(((1, 2), str), (3, bool))
    def map_attribute(self, name, mapped_name, is_time_key=False):
        """
        map_attribute(self, name, mapped_name, is_time_key=False)

        .. seealso:: :func:`TimeSeries.map_attribute`

        :param name: Original name of the attribute/column in CSV file.
        :type name: str
        :param mapped_name: New name for the attribute.
        :type mapped_name: str

        """
        super(TimeSeriesObject, self).map_attribute(name, mapped_name, is_time_key)
        self._compute_data()

    @accepts((1, str), (2, FunctionType))
    def convert(self, item, converter):
        """
        convert(self, item, converter)

        Convert each element of the list mapped by ``item`` with the ``convert``
        function.

        :param item: the key of the list to convert
        :type item: str

        :param converter: the conversion function
        :type converter: function

        """
        super(TimeSeriesObject, self).convert(item, converter)
        self._compute_data()

    def __getattr__(self, item):

        if self._computed_data is None:
            self._compute_data()

        if item in self._computed_data:
            return self._computed_data[item][self._index]
        else:
            raise AttributeError(str(item)+" attribute does not exist")

    @units.wraps(None, (None, units.second), strict=False)
    def set_time(self, time=0):
        """
        set_time(self, time=0)

        Changes the actual time on the object.

        :param time: the new time.
        :type time: float, int or time, see :mod:`gridsim.unit`
        """
        if self._computed_data is None:
            self._compute_data()

        if time in self._computed_data[self._time_key]:
            self._index = time
        else:
            self._index = min(self._computed_data[self._time_key],
                              key=lambda i: abs(i-time))

    @accepts((1, (str, BufferedReader)),
             (2, (None, FunctionType)),
             (3, str))
    def load(self, stream, time_converter=None, time_key='time'):
        """
        load(self, stream, time_converter=None, time_key='time')

        :param stream:
        :param time_converter:
        :param time_key:
        :return:
        """
        self._data = self._reader.load(stream, data_type=float)

        self._time_key = time_key

        if self._time_key in self._data:
            if time_converter is None:
                self.convert(self._time_key, lambda t: t*units.second)
            else:
                self.convert(self._time_key, time_converter)

        else:
            warnings.warn("The data {0} has no '{1}' values".
                          format(stream, time_key),
                          category=SyntaxWarning)

        self._compute_data()

    def _compute_data(self):
        """
        _compute_data(self)

        Computes data, after a call of :func:`TimeSeriesObject.load`.
        """

        self._computed_data = {}

        time_list = self._data[self._time_key]

        for key in self._data.keys():
            self._computed_data[key] = {}
            data_list = self._data[key]

            computed_data = {}
            for time, data in zip(time_list, data_list):
                computed_data[
                    units.value(units.convert(time, units.second))
                ] = data

            self._computed_data[key] = computed_data


class SortedConstantStepTimeSeriesObject(TimeSeries):

    @accepts((1, Reader))
    def __init__(self, reader):
        """
        __init__(self, reader)

        This class is a time series with a constant time step between each data.
        """
        super(SortedConstantStepTimeSeriesObject, self).__init__(reader)

        self._start = 0
        self._interval = 1
        self._count = 0

    def __getattr__(self, item):
        if item in self._data:
            return self._data[item][self._index]
        else:
            raise AttributeError(str(item)+" attribute does not exist")

    @accepts(((1, 2), str), (3, bool))
    def map_attribute(self, name, mapped_name, is_time_key=False):
        """
        map_attribute(self, name, mapped_name, is_time_key=False)

        .. seealso:: :func:`TimeSeries.map_attribute`

        :param name: Original name of the attribute/column in CSV file.
        :type name: str
        :param mapped_name: New name for the attribute.
        :type mapped_name: str

        """
        super(SortedConstantStepTimeSeriesObject, self).\
            map_attribute(name, mapped_name, is_time_key)

        if is_time_key:
            self._update_parameters()

    @units.wraps(None, (None, units.second), strict=False)
    def set_time(self, time=0):
        """
        set_time(self, time=0)

        Changes the actual time on the object.

        :param time: the new time.
        :type time: float, int or time, see :mod:`gridsim.unit`
        """
        time_value = units.value(units.convert(time, units.seconds))

        if time_value < self._start:
            self._index = -1
        else:
            self._index = int((time_value - self._start) / self._interval) % self._count

    @accepts((1, (str, BufferedReader)),
             (2, (None, types.MethodType)),
             (3, str))
    def load(self, stream, time_converter=None, time_key='time'):

        self._data = self._reader.load(stream, data_type=float)
        self._time_key = time_key

        if self._time_key in self._data:
            if time_converter is None:
                self.convert(self._time_key, lambda t: t*units.second)
            else:
                self.convert(self._time_key, time_converter)

            self._update_parameters()

        else:
            warnings.warn("The data {0} has no '{1}' values".
                          format(stream, time_key),
                          category=SyntaxWarning)

    def _update_parameters(self):
        """
        This function update the internal parameters of the class.

        Currently, converting in int instead of using units to improve execution
        speed.
        """
        self._start = units.value(units.convert(min(self._data[self._time_key]),
                                                units.seconds))
        self._count = units.value(units.convert(len(self._data[self._time_key]),
                                                units.seconds))
        self._interval = units.value(units.convert(
            self._data[self._time_key][1] - self._data[self._time_key][0],
            units.seconds))
