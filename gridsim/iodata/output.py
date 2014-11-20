import os

import matplotlib.pyplot as plot

from gridsim.decorators import accepts, returns


class AttributesGetter(object):
    """

    """

    def __init__(self):
        super(AttributesGetter, self).__init__()

    @returns(list)
    def get_x_values(self):
        """
        This method returns x values of data stored.

        :return: a list of values
        :rtype: list
        """
        raise NotImplementedError('Pure abstract method.')

    @returns(str)
    def get_x_unit(self):
        """
        This method returns x unit of data stored.

        :return: a string representing the unit.
        :rtype: str
        """
        raise NotImplementedError('Pure abstract method.')

    @returns(dict)
    def get_y_values(self):
        """
        This method returns y values of data stored. As more than one data can
        be sent, the values have to be sent with the following format:
        `[(label1, data1), (label2, data2), ...]`
        with:
            * labelX: a string representing the dataX
            * dataX: a list of data

        :return: a dict of values
        :rtype: dict
        """
        raise NotImplementedError('Pure abstract method.')

    @returns(str)
    def get_y_unit(self):
        """
        This method returns y unit of data stored.

        :return: a string representing the unit.
        :rtype: str
        """
        raise NotImplementedError('Pure abstract method.')


class FigureSaver(object):

    @accepts((1, AttributesGetter),
             ((2, 3), str))
    def __init__(self, values, title):
        """
        A :class:`PlotRecorder` can be used to record one or multiple signals
        and plot them at the end of the simulation either to a image file,
        add them to a PDF or show them on a window.

        :param values: The values to display
        :type values: AttributesGetter

        :param title: The title of the plot.
        :type title: str

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
        super(FigureSaver, self).__init__()

        self._title = title
        self._figure = None

        self._x_unit = values.get_x_unit()
        self._x = values.get_x_values()
        self._y_unit = values.get_y_unit()
        self._y = values.get_y_values()

    @property
    def figure(self):
        """
        Returns the matplotlib figure identifier. If the figure was not already
        rendered, it will do this by calling :func:`render()` automatically
        before actually returning the figure.

        :returns: matplotlib figure.
        """
        if self._figure is None:
            self.render()
        return self._figure

    @accepts(((1, 2), (type(None), int, float)))
    def render(self, y_min=None, y_max=None):
        """
        Does the actual figure and returns the matplotlib figure identifier.
        Note that you do not need to call this method explicitly as it will
        get called as soon as needed by other methods like :func:`save()` or the
        property getter **figure** are called. This method offers some
        fine tuning parameters to control the look of the figure.

        :param y_min: Minimal value on the y-axis.
        :type y_min: float

        :param y_max: Maximal value on the y-axis.
        :type y_max: float
        """
        self._figure = plot.figure()
        plot.title(self._title)
        if (y_min is not None) and (y_max is not None):
            plot.ylim(y_min, y_max)
        for meta, data in self._y.iteritems():
            plot.plot(self._x, data, label=meta)
        plot.xlabel('[' + self._x_unit + ']')
        plot.ylabel('[' + self._y_unit + ']')
        plot.legend(loc='best', prop={'size': 8})
        return self._figure

    @accepts((1, str))
    def save(self, file_name):
        """
        Saves the figure in the given file (file_name). The format is deduced
        from the file name extension. The output supported formats available
        depend on the backend being used. On Unix systems these formats are
        normally supported:

            **Scalable Vector Graphics** - \*.svg, \*.svgz (zip \*.svg)

            **Graphics Interchange Format** - \*.gif

            **Portable Network Graphics** - \*.png

            **JPEG Image** - \*.jpg, \*.jpeg

            **Postscript** - \*.ps

            **Encapsulated Postscript** - \*.eps

            **Tagged Image Format File** - \*.tif, \*.tiff

            **Raw RGBA bitmap** - \*.raw, \*.rgba

            **Portable Document Format** - \*.pdf

        :param file_name: File name (path) where to save the figure. The file
            format is deduced from the file extension.
        :type file_name: str
        """
        self.figure.savefig(file_name)


class CSVSaver(object):

    @accepts((1, AttributesGetter),
             (2, str))
    def __init__(self, values, separator=','):
        """
        :param values: The values to display
        :type values: AttributesGetter

        """
        super(CSVSaver, self).__init__()

        self._figure = None
        self._separator = separator

        self._x_unit = values.get_x_unit()
        self._x = values.get_x_values()
        self._y_unit = values.get_y_unit()
        self._y = values.get_y_values()

    @accepts((1, str))
    def save(self, file_name):

        save_file = open(file_name, 'w')

        header = str(self._x_unit)+self._separator + \
            self._separator.join([str(key) for key in self._y.keys()])

        header += os.linesep
        save_file.writelines(header)

        for i in range(0, len(self._x)):
            data = str(self._x[i])+self._separator + \
                self._separator.join([str(v[i]) for v in self._y.values()])

            data += os.linesep
            save_file.writelines(data)

        save_file.close()