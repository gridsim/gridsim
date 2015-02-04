"""
.. moduleauthor:: Michael Clausen <clm@hevs.ch>
.. codeauthor:: Michael Clausen <clm@hevs.ch>
.. codeauthor:: Gillian Basso <gillian.basso@hevs.ch>

The :mod:`gridsim.recorder` module allows to record signals within the
gridsim simulation for later analysis. The module offers already a great
number of ready to use recorders - for example to write the data to text or
csv files or to plot the data after the simulation.

However if a special behavior is needed, custom recorders implementing the
:class:`.Recorder` can be implemented.

*Here an example illustrating the implementation of a custom recorder and how
recorders are added to the simulation:*

.. literalinclude:: ../../demo/consolerecorder.py
    :linenos:

- On lines 8 to 23 we implement our custom recorder.

  - On lines 13 & 14 we re-implement the abstract method
    :func:`gridsim.simulation.Recorder.on_simulation_reset`.
    We log which objects we observe.
  - On lines 16 to 18 we implement the
    :func:`gridsim.simulation.Recorder.on_simulation_step` method.
    We just output the current time. The time is given in a float in second.
  - On lines 20 to 23 we re-implement the abstract method
    :func:`gridsim.simulation.Recorder.on_observed_value()`.
    Basically we just output the value to the console. The time is given in a
    float in second.

- On line 26 we create the gridsim simulation object.
- On lines 37 to 51 we setup a very simple thermal process, where we define 2
  rooms and a thermal coupling between them:

  - hot_room (line 38) has a ``surface`` of ``50m2`` and a ``height`` of
    ``2.5m``, so the ``volume`` is ``125m3``. The room is filled with
    :class:`gridsim.util.Air` (specific thermal capacity=`1005 J/kgK``) with
    the initial temperature of 60 degree celsius (line 38).
  - cold_room (line 44) has the same volume, but an initial temperature of 20
    degree celsius (line 43).
  - the two rooms are coupled with a thermal conductivity of ``100 Watts per
    Kelvin`` (lines 49 to 51).

- On lines 55 & 56 we add the recorder to the simulation. The recorder will
  listen all :class:`ThermalProcess` and record their ``temperature`` parameter.
  The horizontal unit will be in second and the vertical unit in degree celsius.
  The simulation will call the recorder's
  **on_simulation_step()** and **on_observed_value()** method each time the
  simulation did a step.

- On line 59 we actually start the simulation for 1 hour with a resolution
  of 5 minutes.

*The output of the console logger should be something like this*::

    RESET, observing: ['hot_room', 'cold_room']
    time = 0 second:
        hot_room.temperature = 60.0 degC
        cold_room.temperature = 20.0 degC
    time = 300.0 second:
        hot_room.temperature = 52.039800995 degC
        cold_room.temperature = 27.960199005 degC
    time = 600.0 second:
        hot_room.temperature = 47.2478404 degC
        cold_room.temperature = 32.7521596 degC
    time = 900.0 second:
        hot_room.temperature = 44.363127803 degC
        cold_room.temperature = 35.636872197 degC
    time = 1200.0 second:
        hot_room.temperature = 42.6265595232 degC
        cold_room.temperature = 37.3734404768 degC
    time = 1500.0 second:
        hot_room.temperature = 41.581162698 degC
        cold_room.temperature = 38.418837302 degC
    time = 1800.0 second:
        hot_room.temperature = 40.9518442113 degC
        cold_room.temperature = 39.0481557887 degC
    time = 2100.0 second:
        hot_room.temperature = 40.5730007441 degC
        cold_room.temperature = 39.4269992559 degC
    time = 2400.0 second:
        hot_room.temperature = 40.3449407464 degC
        cold_room.temperature = 39.6550592536 degC
    time = 2700.0 second:
        hot_room.temperature = 40.2076508971 degC
        cold_room.temperature = 39.7923491029 degC
    time = 3000.0 second:
        hot_room.temperature = 40.1250037739 degC
        cold_room.temperature = 39.8749962261 degC
    time = 3300.0 second:
        hot_room.temperature = 40.0752510281 degC
        cold_room.temperature = 39.9247489719 degC
    time = 3600.0 second:
        hot_room.temperature = 40.0453003701 degC
        cold_room.temperature = 39.9546996299 degC
"""
from math import floor

from gridsim.iodata.output import AttributesGetter

from .unit import units
from .decorators import accepts, returns
from .simulation import Recorder


class PlotRecorder(Recorder, AttributesGetter):

    @accepts((1, str), ((2, 3), (units.Quantity, type, type(None))))
    def __init__(self, attribute_name, x_unit=None, y_unit=None):
        """
        __init__(self, attribute_name, x_unit=None, y_unit=None)

        A :class:`PlotRecorder` can be used to record one or multiple signals
        and plot them at the end of the simulation either to a image file,
        add them to a PDF or show them on a window.

        :param attribute_name: The attribute name to observe. Every
            :class:`.AbstractSimulationElement` with a param of this name can
            be recorded
        :type attribute_name: str
        :param x_unit: The unit of the horizontal axis
        :type x_unit: int, float, type or unit see :mod:`gridsim.unit`
        :param y_unit: The unit of the vertical axis
        :type y_unit: int, float, type or unit see :mod:`gridsim.unit`

        If no information are give to the constructor of a :class:`.Recorder`,
        the data are not preprocessed.

        .. warning:: The preprocess can take a long time if a lot of data are
                     stored in a :class:`.PlotRecorder`.

        *Example:*

        .. literalinclude:: ../../demo/plotrecorder.py
            :linenos:

        * In this example, only new concept are detailed.
        * On line 46, we create a :class:`PlotRecorder` which recorder the
          ``temperature`` attribute in Kelvin.
        * On line 47, we use that recorder in order to record all elements in
          the thermal module who have the attribute 'temperature' by using the
          powerful :func:`gridsim.simulation.Simulator.find()` method by asking
          to return a list of all elements that have the attribute 'temperature'.
        * On line 51, we create a very similar recorder as before, but
          the attribute will be in celsius and the time in minutes.
        * On line 52, we recorder same objects as above,
        * On line 68, we create a first :class:`.FigureSaver` instance with the
          title 'Temperature (K)' which will use the data returned by the
          :class:`.Recorder` to :func:`save` the data in a figure.
        * On line 69, we also save the data of the other :class:`.Recorder`.
          The figures below show that the result is quite the same except that
          the y-coordinates have the right unit.
        * On line 72, we save the data using another saver: :class:`.CSVSaver`.

        The resulting 3 images of this simulation are show here:

        .. figure:: ../../demo/output/fig1.png
            :align: center

        .. figure:: ../../demo/output/fig2.png
            :align: center

        .. figure:: ../../demo/output/fig3.png
            :align: center

        """
        super(PlotRecorder, self).__init__(attribute_name, x_unit, y_unit)

        self._x = []
        self._y = {}

        # for optimisation when getting results
        self._res_x = []
        self._res_y = {}

    def on_simulation_reset(self, subjects):
        """
        on_simulation_reset(self, subjects)

        :class:`.Recorder` implementation. Prepares the data structures.

        .. seealso:: :func:`gridsim.simulation.Recorder.on_simulation_reset()`
                     for details.
        """
        for subject in subjects:
            self._y[subject] = []

    @accepts((1, (int, float)))
    def on_simulation_step(self, time):
        """
        on_simulation_step(self, time)

        :class:`.Recorder` implementation. Prepares the data structures.

        .. seealso:: :func:`gridsim.simulation.Recorder.on_simulation_step()`
                     for details.
        """
        self._x.append(time)

    @accepts((2, (int, float)), (3, (int, float, units.Quantity)))
    def on_observed_value(self, subject, time, value):
        """
        on_observed_value(self, subject, time, value)

        :class:`.Recorder` implementation. Saves the data in order to
        plot them afterwards.

        .. seealso:: :func:`gridsim.simulation.Recorder.on_observed_value()`
                     for details.
        """
        self._y[subject].append(value)

    def x_values(self):
        """
        x_values(self)

        Retrieves a list of time, on for each :func:`on_observed_value` and
        ordered following the call of :func:`gridsim.simulation.Simulator.step`.

        *Example*::

            sim = Simulator()

            kelvin = PlotRecorder('temperature')
            sim.record(kelvin, sim.thermal.find(has_attribute='temperature'))

            sim.step(17*units.second)
            sim.step(5*units.second)
            sim.step(42*units.second)

        In this example, this function should returns::

            [17, 5, 42]

        :return: time in second
        :rtype: list
        """
        if self._x_unit is None:
            self._res_x = self._x
        elif self._res_x is None or not len(self._res_x) == len(self._x):
            self._res_x = [units.value(units.convert(x, units.to_si(self._x_unit)), self._x_unit)
                           for x in self._x]
        return self._res_x

    @returns(str)
    def x_unit(self):
        """
        x_unit(self)

        Retrieves the unit of the time.

        :return: the time unit, see :mod:`gridsim.unit`
        :rtype: str
        """
        if type(self._x_unit) is units.Quantity:
            return units.unit(self._x_unit)
        else:
            return str(self._x_unit)

    def y_values(self):
        """
        y_values(self)

        Retrieves a map of the recorded data::

            {
                id1: [list of recorded values]
                id2: [list of recorded values]
            }

        with ``idX`` the ``subject`` given in parameter of :func:`on_observed_value`
        and :func:`on_simulation_reset`

        :return: a map associating id to recorded data
        :rtype: dict
        """
        if self._y_unit is None:
            self._res_y = self._y
        elif self._res_y is None or not len(self._res_y) == len(self._y):
                self._res_y = {}
                for key in self._y.keys():
                    if type(self._y_unit) is type:
                        self._res_y[key] = [self._y_unit(y) for y in self._y[key]]
                    else:
                        self._res_y[key] = [units.value(units.convert(y, units.to_si(self._y_unit)), self._y_unit)
                                            for y in self._y[key]]

        return self._res_y

    @returns(str)
    def y_unit(self):
        """
        y_unit(self)

        Retrieves the unit od the recorded data.

        :return: the type or the unit, see :mod:`gridsim.unit`
        :rtype: str
        """
        if type(self._y_unit) is units.Quantity:
            return units.unit(self._y_unit)
        else:
            return str(self._y_unit)


class HistogramRecorder(Recorder, AttributesGetter):

    @accepts((1, str),
             (4, int),
             ((5, 6), type))
    def __init__(self, attribute_name, x_min, x_max, nb_bins, x_unit, y_unit):
        """
        .. warning:: This class is currently not tested...

        :param attribute_name:
        :param x_min:
        :param x_max:
        :param nb_bins:
        :param x_unit: The unit of the horizontal axis
        :type x_unit: type or unit see :mod:`gridsim.unit`
        :param y_unit: The unit of the vertical axis
        :type y_unit: type
        :return:
        """
        if x_max <= x_min:
            raise TypeError("'x_max' must be larger than 'x_min'.")

        super(HistogramRecorder, self).__init__(attribute_name, x_unit, y_unit)

        self._x_min = x_min
        self._x_max = x_max
        self._N_bins = nb_bins
        self._x_delta = (x_max - x_min) / (nb_bins - 2)
        self._y = {}

    def on_simulation_reset(self, subjects):
        """
        :class:`RecorderInterface` implementation. Writes the header to the file
        defined by the _header_format attribute each time the simulation does a
        reset.

        .. seealso:: :func:`RecorderInterface.on_simulation_reset()`
                     for details.
        """
        for subject in subjects:
            label = subject + "." + self.attribute_name
            self._y[label] = [0 for _ in xrange(self._N_bins)]

    def on_simulation_step(self, time):
        """
        :class:`RecorderInterface` implementation. Called for each simulation
        step once per recorder.
        Writes the step separation to the file.

        .. seealso:: :func:`RecorderInterface.on_simulation_step()` for details.
        """
        pass

    def on_observed_value(self, subject, time, value):
        """
        :class:`RecorderInterface` implementation. Writes a (formatted) string
        into the file.

        .. seealso:: :func:`RecorderInterface.on_observed_value()` for details.
        """

        if value < self._x_min.total_seconds():
            bin_i = 0
        elif value >= self._x_max.total_seconds():
            bin_i = self._N_bins - 1
        else:
            bin_i = 1 + int(floor((value - self._x_min.total_seconds()) /
                                  self._x_delta))
        label = subject + "." + self.attribute_name
        self._y[label][bin_i] += 1

    def x_values(self):
        return []

    @returns(str)
    def x_unit(self):
        return ""

    def y_values(self):
        return self._y

    @returns(str)
    def y_unit(self):
        return self._y_unit
