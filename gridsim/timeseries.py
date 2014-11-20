"""
.. moduleauthor:: Michael Clausen <clm@hevs.ch>

FIXME : review comments

The timeseries module allows to import time series based data from CSV into
objects as attributes. The format of the CSV files is common CSV syntax where
each row starts with a new line and columns are separated using ';'. The only
constraint to the file is the first line has to contain some meta information
about the file itself in the format::

<start time in seconds>;<interval in seconds>;<column attribute names separated by ','>

*Example:*::

    0;60;temperature,humidity
    20.0;0.2
    20.0;0.25
    18.5;0.1
    ...

This would be a file containing two time series, **temperature** and
**humidity**. The values start at 0 seconds in the simulation and the
interval (line to next line in file) is one minute (60 seconds).

The data inside the files are translated into attributes for the
:class:`TimeSeriesObject` by calling the :func:`TimeSeriesObject.load` method
on a TimeSeriesObject or any subclass of it::

    obj = TimeSeriesObject()
    obj.load('../../data/examples/example.csv')

The complete data of the file is now loaded into the object. If the content of
the file test.csv would be the text above, the column names turn into
attributes::

    print obj.temperature

Would give the output::

    20.0

Now we can set the time on the object in order to get different values in time::

    obj.set_time(120)
    print obj.temperature

This would give an output like this::

    18.5

*Here the listing of the complete example:*

.. literalinclude:: ../../demo/timeseries.py
    :linenos:
"""
import types
import warnings
from io import BufferedReader

from types import FunctionType

from .decorators import accepts
from .unit import units
from .iodata.input import Reader


class TimeSeriesObject(object):

    @accepts((1, Reader))
    def __init__(self, reader):
        """
        The time series objects allows to load data from CSV file into a Python
        object and allows to access these in a very simple way by providing
        them as attributes.

        *Example*:

        .. literalinclude:: ../demos/timeseries2.py

        The result of the script:

        .. figure:: timeseries-example.png
            :align: center
        """
        super(TimeSeriesObject, self).__init__()

        self._reader = reader
        self._data = None
        self._index = 0
        self._time_key = 'time'

    @accepts(((1, 2), str))
    def map_attribute(self, name, mapped_name):
        """
        If the attribute name of the file does not match the target attribute
        name for the object, you can use this method to map the original name to
        a new attribute name.

        .. warning:: The old mapping will be removed.


        *Example*::

            obj.map('temperature', 'temp')

        The example will change the name of the attribute mapped to the data
        column from 'temperature' to 'temp'.

        .. warning:: the old value is delete from the TimeSeries

        :param name: Original name of the attribute/column in CSV file.
        :type name: str
        :param mapped_name: New name for the attribute.
        :type mapped_name: str

        """

        if name not in self._data:
            raise AttributeError('No such attribute {0}'.format(name))
        if mapped_name in self._data:
            raise AttributeError(
                'Can not map attribute {0}, as it exists already.'.format(
                    mapped_name))

        if name is self._time_key:
            self._time_key = mapped_name

        self._data[mapped_name] = self._data.pop(name)

    def __getattr__(self, item):
        if self._index < 0:
            raise IndexError("Index cannot be negative: "+str(self._index))
        if item in self._data:
            return self._data[item][self._index]
        else:
            raise AttributeError(str(item)+" attribute does not exist")

    def set_time(self, time=0*units.second):
        """
        Changes the actual time on the object.

        :param time: Time.
        :type time: float, int

        """
        tmp_value = next((t for t in reversed(self._data[self._time_key])
                          if t <= time),
                         -1)  # FIXME takes too long

        self._index = self._data[self._time_key].index(tmp_value)

    @accepts((1, str), (2, FunctionType))
    def convert(self, item, converter):
        """
        Convert each element of the list mapped by `item` with the `convert`
        function.

        :param item: the key of the list to convert
        :type item: str

        :param converter: the conversion function
        :type converter: function

        """
        self._data[item] = map(converter, self._data[item])

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
        else:
            warnings.warn("The data {0} has no '{1}' values".
                          format(stream, time_key),
                          category=SyntaxWarning)
