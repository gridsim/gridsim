"""
.. moduleauthor:: Gilbert Maitre <gilbert.maitre@hevs.ch>

The :mod:`gridsim.electrical` module implements the electrical part of the
gridsim simulator. It basically manages Consuming-Producing-Storing (CPS)
Elements, which consume (positive sign) and/or produce (negative sign) a
certain amount of energy ('delta_energy') at each simulation step.

CPS elements may be attach to buses of an electrical power network, which is
also made of branches as connections between buses.

*Example*:

.. literalinclude:: ../../demo/loadflow.py
    :linenos:

shows a pure electrical example made of a reference 5-bus network
(see e.g. Xi-Fan Wang, Yonghua Song, Malcolm Irving, Modern power systems
analysis), to the non-slack buses of which are attached 4 CPS elements :
1 with constant power, production, 3 with random gaussian distributed power
consumption.

"""
import csv

import numpy as np

from gridsim.decorators import accepts
from gridsim.unit import units
from gridsim.timeseries import TimeSeriesObject
from gridsim.iodata.input import Reader

from .core import AbstractElectricalCPSElement


class ConstantElectricalCPSElement(AbstractElectricalCPSElement):

    @accepts((1, str))
    def __init__(self, friendly_name, power):
        """
        This class provides the simplest Consuming-Producing-Storing element
        having a constant behavior.

        This class is based on the 'AbstractElectricalCPSElement' class.
        At initialization, the consumed or produced constant 'power' has to
        be provided beside the element 'friendly_name'. Power is positive, if
        consumed, negative, if produced. With the 'calculate' method the
        energy consumed or produced during the simulation step is calculated
        from the constant power value.

        :param friendly_name: Friendly name for the element. Should be unique
            within the simulation module.
        :type friendly_name: str

        :param power: The constant consumed (if positive) or produced
            (if negative) power.
        :type power: power

        """
        super(ConstantElectricalCPSElement, self).__init__(friendly_name)
        self.power = power

    def calculate(self, time, delta_time):
        """
        Calculate the element's the energy consumed or produced by the element
        during the simulation step.

        :param time: The actual time of the simulator in seconds.
        :type time: timedelta
        :param delta_time: The delta time for which the calculation has to be
            done in seconds.
        :type delta_time: timedelta
        """
        self._internal_delta_energy = self.power * delta_time


class CyclicElectricalCPSElement(AbstractElectricalCPSElement):

    @accepts((1, str),
             ((2, 4), int))
    def __init__(self, friendly_name, cycle_delta_time, power_values,
                 cycle_start_time=0):
        """
        This class provides a Consuming-Producing-Storing element having a
        cyclic behavior.

        This class is based on the 'AbstractElectricalCPSElement' class. At
        initialization, beside the element 'friendly_name', the cycle time
        resolution 'cycle_delta_time', the cycle sequence of 'power_values',
        and the 'cycle_start_time' have to be given.

        :param friendly_name: Friendly name for the element. Should be unique
            within the simulation module.
        :type friendly_name: str

        :param cycle_delta_time: cycle time resolution value in seconds.
        :type cycle_delta_time: int

        :param power_values: power values consumed or produced during a cycle.
        :type power_values: 1-D numpy array of power

        :param cycle_start_time: cycle start time in seconds. Defaults to 0.
        :type cycle_start_time: int

        """
        super(CyclicElectricalCPSElement, self).__init__(friendly_name)

        if power_values.dtype != float:
            raise TypeError("'power_values' has to be an array of floats.")
        if len(power_values.shape) != 1:
            raise RuntimeError(
                "'power_values' has to be a one-dimensional array")

        self._cycle_delta_time = cycle_delta_time
        self._power_values = power_values
        self._cycle_length = len(power_values)
        self._cycle_start_time = cycle_start_time

    @property
    def cycle_delta_time(self):
        """
        Gets the cycle time resolution.

        :returns: cycle time resolution.
        :rtype: int
        """
        return self._cycle_delta_time

    @property
    def power_values(self):
        """
        Gets the cycle power values array.

        :returns: cycle power values array.
        :rtype: 1-dimensional numpy array of float
        """
        return self._power_values

    @property
    def cycle_length(self):
        """
        Gets the cycle length in cycle time resolution units.

        :returns: cycle length in cycle time resolution units.
        :rtype: int
        """
        return self._cycle_length

    @property
    def cycle_start_time(self):
        """
        Gets the cycle start time.

        :returns: cycle start time.
        :rtype: int
        """
        return self._cycle_start_time

    def calculate(self, time, delta_time):
        """
        Calculate the element's the energy consumed or produced by the element
        during the simulation step.

        :param time: The actual time of the simulator in seconds.
        :type time: float
        :param delta_time: The delta time for which the calculation has to be
            done in seconds.
        :type delta_time: float
        """
        current_cycle_pos = int((
                                time - self._cycle_start_time) /
                                self._cycle_delta_time) % self._cycle_length
        self._internal_delta_energy = 0*units.joule
        current_dtime = 0*units.second
        next_dtime = self._cycle_delta_time
        if next_dtime > delta_time:
            next_dtime = delta_time
        while current_dtime < delta_time:
            self._internal_delta_energy += \
                self._power_values[current_cycle_pos] * \
                ((next_dtime - current_dtime) / self._cycle_delta_time)
            current_cycle_pos += 1
            if current_cycle_pos >= self._cycle_length:
                current_cycle_pos = 0
            current_dtime = next_dtime
            next_dtime += self._cycle_delta_time
            if next_dtime > delta_time:
                next_dtime = delta_time
# TODO: verify results


class UpdatableCyclicElectricalCPSElement(CyclicElectricalCPSElement):

    @accepts((1, str),
             ((2, 4), int),
             (3, np.ndarray))
    def __init__(self, friendly_name, cycle_delta_time, power_values,
                 cycle_start_time=0*units.second):
        """
        This class provides a cyclic Consuming-Producing-Storing element for
        which the consumed or produced power values may be updated. Update
        will take place at next cycle start.

        This class is based on the 'CyclicElectricalCPSElement' class.
        At initialization, it takes the same input parameters.

        :param friendly_name: Friendly name for the element.
            Should be unique within the simulation module.
        :type friendly_name: str

        :param cycle_delta_time: cycle time resolution value in seconds.
        :type cycle_delta_time: int

        :param power_values: power values consumed or produced during a cycle.
        :type power_values: 1-D numpy array of float

        :param cycle_start_time: cycle start time in seconds. Defaults to 0.
        :type cycle_start_time: int

        """
        super(UpdatableCyclicElectricalCPSElement, self).\
            __init__(friendly_name, cycle_delta_time,
                     power_values, cycle_start_time)
        self._new_power_values = power_values
        self._update_done = True

    @property
    def power_values(self):
        """
        Gets the cycle power values array.

        :returns: cycle power values array.
        :rtype: 1-dimensional numpy array of float
        """
        return self._power_values

    @power_values.setter
    @accepts((1, np.ndarray))
    def power_values(self, new_power_values):
        if new_power_values.dtype != float:
            raise TypeError("'power_values' has to be an array of floats.")
        if len(new_power_values.shape) != 1:
            raise RuntimeError(
                "'power_values' has to be a one-dimensional array")
        if len(new_power_values) != len(new_power_values):
            raise RuntimeError(
                "cycle length, i.e. length of 'power_values'"
                ", may not be changed")
        self._new_power_values = new_power_values
        self._update_done = False

    def calculate(self, time, delta_time):
        """
        Calculate the element's the energy consumed or produced by the element
        during the simulation step.

        :param time: The actual time of the simulator in seconds.
        :type time: float
        :param delta_time: The delta time for which the calculation has to be
            done in seconds.
        :type delta_time: float
        """
        if not self._update_done:
            current_cycle_pos = \
                int((time - self._cycle_start_time) /
                    self._cycle_delta_time) % self._cycle_length
            if current_cycle_pos == 0:
                self._power_values = self._new_power_values
                self._update_done = True
        super(UpdatableCyclicElectricalCPSElement, self).\
            calculate(time, delta_time)
        # TODO: verify results


class GaussianRandomElectricalCPSElement(AbstractElectricalCPSElement):

    @accepts((1, str))
    def __init__(self, friendly_name, mean_power, standard_deviation):
        """
        This class provides a Consuming-Producing-Storing element having a
        random behavior. The consecutive consumed or produced power values
        are IID (Independently and Identically Distributed). The distribution
        is Gaussian.

        This class is based on the 'AbstractElectricalCPSElement' class.
        At initialization, the 'mean_power' and 'standard_distribution' are
        provided beside the element 'friendly_name'. If 'mean_power' is
        positive, the element is in the mean a consumer. If it is negative,
        the element is in the mean a producer.

        :param friendly_name: Friendly name for the element.
            Should be unique within the simulation module.
        :type friendly_name: str

        :param mean_power: The mean value of the Gaussian distributed power.
        :type mean_power: power

        :param standard_deviation: The standard deviation of the Gaussian
            distributed power.
        :type standard_deviation: power

        """
        super(GaussianRandomElectricalCPSElement, self).__init__(friendly_name)
        self._mean_power = mean_power
        self._standard_deviation = standard_deviation

    @property
    def mean_power(self):
        """
        Gets the mean value of the Gaussian distributed power.

        :returns: mean power value.
        :rtype: float
        """
        return self._mean_power

    @property
    def standard_deviation(self):
        """
        Gets the standard deviation of the Gaussian distributed power.

        :returns: standard deviation value.
        :rtype: float
        """
        return self._standard_deviation

    def calculate(self, time, delta_time):
        """
        Calculate the element's the energy consumed or produced by the element
        during the simulation step.

        :param time: The actual time of the simulator in seconds.
        :type time: timedelta
        :param delta_time: The delta time for which the calculation has to be
            done in seconds.
        :type delta_time: timedelta
        """
        normal_value = np.random.normal(self._mean_power.to(units.watt),
                                        self._standard_deviation.to(units.watt))
        normal = normal_value*units.watt

        self._internal_delta_energy = normal * delta_time


class TimeSeriesElectricalCPSElement(ConstantElectricalCPSElement):

    @accepts(((1, 3), str),
             (2, Reader))
    def __init__(self, friendly_name, reader, stream, column_name='power'):
        """
        This class provides a Consuming-Producing-Storing element whose consumed
        or produced power is read in a column of a csv file.

        This class is based on the 'ConstantElectricalCPSElement' class.
        At initialization, the 'file_name' and the 'attribute_name' are
        provided.

        The attribute is assumed to carry a power value.

        :param friendly_name: Friendly name for the element.
            Should be unique within the simulation module.
        :type friendly_name: str
        :param reader: The data reader
        :type reader: Reader
        :param stream: The file name
        :type stream: str
        :param column_name: The name of the column in the data with a the
            requested power value.
        :type column_name: str

        """
        super(TimeSeriesElectricalCPSElement, self).__init__(friendly_name, 0)

        self._time_series = TimeSeriesObject(reader)
        self._time_series.load(stream)

        # Check whether the file has the requested attribute
        try:
            self._time_series.column_name
        except AttributeError:
            raise AttributeError('Requested column is missing in data')

    def __getattr__(self, item):
        return getattr(self.time_series, item)

    def reset(self):
        """
          AbstractSimulationElement implementation

          .. seealso:: :func:`gridsim.core.AbstractSimulationElement.reset`.
       """
        self._time_series.set_time()

    def calculate(self, time, delta_time):
        """
        Calculate the energy consumed or produced by the element during the
        simulation step.

        :param time: The actual time of the simulator in seconds.
        :type time: float
        :param delta_time: The delta time for which the calculation has to be
            done in seconds.
        :type delta_time: float
        """
        self._time_series.set_time(time)
        self._internal_delta_energy = self._time_series.power * delta_time


class AnyIIDRandomElectricalCPSElement(AbstractElectricalCPSElement):

    @accepts((1, str),
             (2, (str, np.ndarray)),
             (3, (type(None), np.ndarray)))
    def __init__(self, friendly_name, fname_or_power_values, frequencies=None):
        """
        This class provides a Consuming-Producing-Storing element having a
        random behavior. The consecutive consumed or produced power values
        are IID (Independently and Identically Distributed). The distribution,
        discrete and finite, is given as parameter.

        This class is based on the 'AbstractElectricalCPSElement' class. Beside
        the element 'friendly_name', the constructor parameters are either
        the name of the file the distribution has to be read from, either the
        potentially consumed or produced 'power_values',together with their
        'frequencies' or probabilities. Input 'power values' has to be a
        monotonically increasing sequence of float. Input 'frequencies' can be
        either integers (number of occurrences), or floats summing to 1.0
        (relative frequencies or probabilities), or monotonically increasing
        sequence of positive floats ending with 1.0 (cumulative relative
        frequencies or probabilities)

        :param friendly_name: Friendly name for the element.
            Should be unique within the simulation module.
        :type friendly_name: str

        :param fname_or_power_values: Name of the file from which the
            distribution has to be read or Power values which may be consumed
            (positive) or produced (negative), ordered in a monotonically
            increasing sequence.
        :type fname_or_power_values: either string or 1-D numpy array of float

        :param frequencies: Number of occurrences (frequencies), or relative
            frequencies, or cumulative relative frequencies of corresponding
            power values, if those are given as second parameter, None if
            filename is given as 2nd parameter
        :type frequencies: None or 1-D numpy array of integer or float
        """
        super(AnyIIDRandomElectricalCPSElement, self).__init__(friendly_name)
        # if first parameter is a string (name of a file), read data
        if isinstance(fname_or_power_values, str):
            if not frequencies is None:
                raise RuntimeError(
                    "'frequencies' cannot be passed as argument, they are read "
                    "from file with name '" + fname_or_power_values +
                    "' in this case")
            [power_values, frequencies] = self._read_hist_from_file(
                fname_or_power_values)
        else:
            power_values = fname_or_power_values  # just copy variable
        # check
        if power_values.dtype != float:
            raise TypeError("'power_values' has to be an array of floats.")
        if len(power_values.shape) != 1:
            raise RuntimeError(
                "'power_values' has to be a one-dimensional array")
        if not frequencies.dtype in (int, float):
            raise TypeError(
                "'frequencies' has to be an array of integers or floats.")
        if len(frequencies.shape) != 1:
            raise RuntimeError(
                "'frequencies' has to be a one-dimensional array")
        if frequencies.shape[0] != power_values.shape[0]:
            raise RuntimeError(
                "'frequencies' and 'power_values' must have the same length")
        self._power_values = power_values
        if frequencies[-1] == 1.0:
            for i_pos in range(1, frequencies.shape[0]):
                if frequencies[i_pos] <= frequencies[i_pos - 1]:
                    raise RuntimeError(
                        "cumulative relative 'frequencies' should be "
                        "monotonically increasing.")
            self._cdf = frequencies
        else:
            if frequencies.dtype == int:
                frequencies.astype('float')
            sum_freq = sum(frequencies)
            if sum_freq == 0.:
                raise TypeError(
                    "sum of values in 'frequencies' may not be zero.")
            self._cdf = np.cumsum((1.0 / sum_freq) * frequencies)

    @accepts((1, str))
    def _read_hist_from_file(self, fname):
        # read file as csv
        with open(fname, 'rb') as csv_file:
            # Create the CSV parser.
            data = csv.reader(csv_file, delimiter=';')
            # Read header. MUST have a length of 3!
            header = data.next()
            if len(header) is not 3:
                raise RuntimeError('Invalid histogram file.')
            # Initialize output
            power_values = []
            frequencies = []
            current_pwr_value = float(header[0])
            delta_pwr_value = float(header[1])
            # Parse data and fill up array
            for row in data:
                power_values.append(current_pwr_value)
                frequencies.append(float(row[0]))
                current_pwr_value += delta_pwr_value

            return np.array(power_values), np.array(frequencies)

    @property
    def power_values(self):
        """
        Gets the sequence of power values which may occur.

        :returns: sequence of potentially occurring power values.
        :rtype: 1-dimensional numpy array of float
        """
        return self._power_values

    @property
    def cdf(self):
        """
        Gets the cumulative relative frequencies of the potentially occurring
        power values. It can be considered as the Cumulative Distribution
        Function (CDF).

        :returns: cumulative relative frequencies corresponding to power values.
        :rtype: 1-dimensional numpy array of float
        """
        return self._cdf

    def calculate(self, time, delta_time):
        """
        Calculate the element's the energy consumed or produced by the element
        during the simulation step.

        :param time: The actual time of the simulator in seconds.
        :type time: float
        :param delta_time: The delta time for which the calculation has to be
            done in seconds.
        :type delta_time: float
        """
        self._internal_delta_energy = \
            self._power_values[np.searchsorted(self._cdf,
                                               np.random.random())] * delta_time

