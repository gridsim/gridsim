# TODO: After a short discussion we would like to change the following:
# TODO: - PlotRecorder -> MemoryRecorder with plot methods or even separated Plot class
# TODO: - Performance improvements for data dictionaries (not replacing each simulation step values).
# TODO: - Maybe better name as "record" for the method to add a recorder to the simulation.
# TODO: - Add preprocessing possibility to basic recorder in order to increase flexibility (would make HistogramRecorder
# TODO: obsolete).

"""
.. moduleauthor:: Michael Clausen <clm@hevs.ch>

The :mod:`gridsim.recorder` module allows to record signals within the
gridsim simulation for later analysis. The module offers already a great
number of ready to use recorders - for example to write the data to text or
csv files or to plot the data after the simulation.

However if a special behavior is needed, custom recorders implementing the
:class:`RecorderInterface` can be implemented.

*Here an example illustrating the implementation of a custom recorder and how
recorders are added to the simulation:*

.. literalinclude:: ../../demo/consolerecorder.py
    :linenos:

- On line 7 to 15 we implement our custom recorder.

  - On line 8 we re-implement the abstract method **on_simulation_reset()**.
    We log which objects we observe.
  - On line 11 we implement the **on_simulation_step()** method.
    We just output the current time.
  - On line 14 we re-implement the abstract method **on_observer_value()**.
    Basically we just output the value to the console.

- On line 18 we create the gridsim simulation object.
- On line 27 to 29 we setup a very simple thermal process, where we define 2
    rooms and a thermal coupling between them:

  - hot_room (line 27) has a **surface of 50m2** and a **height of 2.5m**, so
    the **volume is 125m3**. The room is filled with air (specific thermal
    capacity=1.005 J/gK) with the **initial temperature of 60 degree celsius**.
  - cold_room (line 28) has the same volume, but an initial **temperature of 20
    degree celsius**.
  - the two rooms are coupled with a thermal conductivity of **100 Watts per
    Kelvin** (line 29).

- On line 32 we add a new recorder (of our custom recorder class) to the
    attribute **temperature** of all ThermalProcesses. That is all we have
    actually to do to add a recorder, the simulation will call the recorder's
    **on_simulation_step()** and **on_observed_value()** method each time the
    simulation did a step.

- On line 35 we actually start the simulation for 1 hour with a resolution
    of 5 minutes.

*The output of the console logger should be something like this*::

    RESET, observing: [<gridsim.thermal.ThermalProcess object at 0x108228310>,
    <gridsim.thermal.ThermalProcess object at 0x108228810>]
    time = 0.0s:
        hot_room.temperature = 60.0
        cold_room.temperature = 20.0
    time = 300.0s:
        hot_room.temperature = 52.039800995
        cold_room.temperature = 27.960199005
    time = 600.0s:
        hot_room.temperature = 47.2478404
        cold_room.temperature = 32.7521596
    time = 900.0s:
        hot_room.temperature = 44.363127803
        cold_room.temperature = 35.636872197
    time = 1200.0s:
        hot_room.temperature = 42.6265595232
        cold_room.temperature = 37.3734404768
    time = 1500.0s:
        hot_room.temperature = 41.581162698
        cold_room.temperature = 38.418837302
    time = 1800.0s:
        hot_room.temperature = 40.9518442113
        cold_room.temperature = 39.0481557887
    time = 2100.0s:
        hot_room.temperature = 40.5730007441
        cold_room.temperature = 39.4269992559
    time = 2400.0s:
        hot_room.temperature = 40.3449407464
        cold_room.temperature = 39.6550592536
    time = 2700.0s:
        hot_room.temperature = 40.2076508971
        cold_room.temperature = 39.7923491029
    time = 3000.0s:
        hot_room.temperature = 40.1250037739
        cold_room.temperature = 39.8749962261
    time = 3300.0s:
        hot_room.temperature = 40.0752510281
        cold_room.temperature = 39.9247489719
    time = 3600.0s:
        hot_room.temperature = 40.0453003701
        cold_room.temperature = 39.9546996299
"""
from math import floor

from gridsim.iodata.output import AttributesGetter

import unit
from .decorators import accepts
from .simulation import Recorder


class PlotRecorder(Recorder, AttributesGetter):

    @accepts((1, str))
    def __init__(self, attribute_name):
        """
        A :class:`PlotRecorder` can be used to record one or multiple signals
        and plot them at the end of the simulation either to a image file,
        add them to a PDF or show them on a window.

        :param attribute_name: The attribute name to observe. Every
            :class:`AbstractSimulationElement` with a param of this name can
            be recorded
        :type attribute_name: str

        *Example:*

        .. literalinclude:: ../../demos/plotrecorder.py
            :linenos:

        * On line 24 we create a PlotRecorder with the title 'Temperatures'
            which uses minutes as the unit for the x-axis. As the title already
            suggest that the signals are temperatures, we only take the
            element's name as the legend format.
        * On line 25 we use that recorder in order to record all elements in the
            thermal module who have the attribute 'temperature' by using the
            powerful :func:`gridsim.core.Simulator.find()` method by asking to
            return a list of all elements that have the attribute 'temperature'.
            We specify with the second argument that we like to read the
            attribute 'temperature' from all objects returned by find().
            Additionally we can specify the physical unit of the data when
            adding a recorder. Note that PlotRecorders demand by their nature
            that all recorded signals (attributes) have the same unit.
        * On line 28 and the following we create a very similar recorder as
            before, but this time we do not want to record the temperature in
            degrees celsius, we want the temperature in kelvin. As the
            ThermalProcess only provides the temperature in degrees celsius we
            have to add a conversion lambda which will be executed every time a
            value is read from the simulation in order to give to the recorder.
            The lambda gets a named tuple as parameter which contains the
            following keys: "value": the value just read from the attribute,
            "time": the actual simulation time and finally "delta_time": the
            time interval for which the value has been calculated. As the
            conversion between degree celsius and kelvin is linear and does
            not depend anything other than the actual value, we can just give
            the lambda expression
        **lambda context: context.value + 273.15**.
        * On line 33 we create a second PlotRecorder instance with the title
            'Thermal power flows' which will show the time axis (x-axis) in
            hours. Again we only show the name of the subject in the legend.
        * On line 34 we attach this recorder to all elements of type (class)
            ThermalCoupling and we setup the recoder to read the 'power'
            attribute. The unit will be Watts (W).
        * On line 37 we run the simulation for 2 hours with a resolution of a
            second.
        * We are saving the plots as image files on line 40 to 43.
        * It is even possible to create a PDF document using the PlotRecorder
            and to append the different plots as new pages onto that
            document. This is done on line 45.

        The resulting 3 images of this simulation are show here:

        .. figure:: plotrecorder-temp.png
            :align: center

        .. figure:: plotrecorder-kelvin.png
            :align: center

        .. figure:: plotrecorder-flow.png
            :align: center

        """
        super(PlotRecorder, self).__init__(attribute_name)

        self._x = []
        self._x_unit = None
        self._y = {}
        self._y_unit = None

    def on_simulation_reset(self, subjects):
        """
        :class:`RecorderInterface` implementation. Prepares the data structures.
        .. seealso:: :func:`RecorderInterface.on_simulation_reset()` for
            details.
        """
        for subject in subjects:
            self._y[subject] = []

    def on_simulation_step(self, time):
        """
        :class:`RecorderInterface` implementation. Prepares the data structures.

        .. seealso:: :func:`RecorderInterface.on_simulation_step()` for details.
        """
        self._x.append(unit.value(time))
        if self._x_unit is None:
            self._x_unit = unit.unit(time)

    def on_observed_value(self, subject, time, value):
        """
        :class:`RecorderInterface` implementation. Saves the data in order to
        plot them afterwards.

        .. seealso:: :func:`RecorderInterface.on_observed_value()` for details.
        """
        self._y[subject].append(unit.value(value))

        if self._y_unit is None:
            self._y_unit = unit.unit(value)

    def get_x_values(self):
        """

        :return: time in second
        """
        return self._x

    def get_x_unit(self):
        """

        :return: second
        """
        return self._x_unit

    def get_y_values(self):
        return self._y

    def get_y_unit(self):
        return self._y_unit


class HistogramRecorder(Recorder, AttributesGetter):

    @accepts((1, str),
             (4, int))
    def __init__(self, attribute_name, x_min, x_max, nb_bins):
        """

        :param attribute_name:
        :param x_min:
        :param x_max:
        :param nb_bins:
        :return:
        """
        if x_max <= x_min:
            raise TypeError("'x_max' must be larger than 'x_min'.")

        super(HistogramRecorder, self).__init__(attribute_name)

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

    def get_x_values(self):
        return []

    def get_x_unit(self):
        return ""

    def get_y_values(self):
        return self._y

    def get_y_unit(self):
        return "count"
