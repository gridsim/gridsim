"""
.. moduleauthor:: Gillian Basso <gillian.basso@hevs.ch>

.. codeauthor:: Michael Clausen <clm@hevs.ch>
.. codeauthor:: Gillian Basso <gillian.basso@hevs.ch>

This module provides interfaces to save data.

To use the :class:`Saver` a class has to implement the :class:`.AttributesGetter`
interface.

*Example:*

.. literalinclude:: ../../demo/plotrecorder.py
    :linenos:

* On lines 46, 51 and 85, we create :class:`.Recorder` objects.
* On lines 47, 52 and 86, we add the recorders to the simulation.
* On lines 69 to 71, we use the recorders as :class:`AttributeGetter` to
  save them in figure. Here, the 3 images file saved:

.. figure:: ../../demo/output/fig1.png
    :align: center

.. figure:: ../../demo/output/fig2.png
    :align: center

.. figure:: ../../demo/output/fig3.png
    :align: center

* On line 73, we use a second saver to save in a csv file the a recorder we
  already saved, here the 20th first lines:

.. literalinclude:: ../../demo/output/fig2.csv
    :linenos:
    :lines: 1-20

"""
import os

import matplotlib.pyplot as plot

from gridsim.decorators import accepts, returns


class AttributesGetter(object):

    def __init__(self):
        """
        __init__(self)

        This is the based class for all data which have to be saved.
        """
        super(AttributesGetter, self).__init__()

    @returns(list)
    def get_x_values(self):
        """
        get_x_values(self)

        This method returns x values of data stored.

        :return: a list of values
        :rtype: list
        """
        raise NotImplementedError('Pure abstract method.')

    @returns(str)
    def get_x_unit(self):
        """
        get_x_unit(self)

        This method returns x unit of data stored.

        :return: a string representing the unit.
        :rtype: str
        """
        raise NotImplementedError('Pure abstract method.')

    @returns(dict)
    def get_y_values(self):
        """
        get_y_values(self)

        This method returns y values of data stored. As more than one data can
        be sent, the values have to be sent with the following format:
        ``[(label1, data1), (label2, data2), ...]``
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
        get_y_unit(self)

        This method returns y unit of data stored.

        :return: a string representing the unit.
        :rtype: str
        """
        raise NotImplementedError('Pure abstract method.')


class FigureSaver(object):

    @accepts((1, AttributesGetter),
             (2, str))
    def __init__(self, values, title):
        """
        __init__(self, values, title)

        A :class:`FigureSaver` can be used to record a class:`.AttributesGetter`
        and plot it in a file.

        :param values: The values to display
        :type values: AttributesGetter

        :param title: The title of the plot.
        :type title: str
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
        The matplotlib figure identifier. If the figure was not already
        rendered, it will do this by calling :func:`render()` automatically
        before actually returning the figure.
        """
        if self._figure is None:
            self.render()
        return self._figure

    @accepts(((1, 2), (type(None), int, float)))
    def render(self, y_min=None, y_max=None):
        """
        render(self, y_min=None, y_max=None)

        Does the actual figure and returns the matplotlib figure identifier.

        .. note:: you do not need to call this method explicitly as it will get
                  called as soon as needed by other methods like :func:`save()`
                  or the property getter **figure** are called. This method
                  offers some fine tuning parameters to control the look of the
                  figure.

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
        plot.xlabel('[' + str(self._x_unit) + ']')
        plot.ylabel('[' + str(self._y_unit) + ']')
        plot.legend(loc='best', prop={'size': 8})
        return self._figure

    @accepts((1, str))
    def save(self, file_name):
        """
        save(self, file_name)

        Saves the figure in the given file (``file_name``). The format is
        deduced from the file name extension. The output supported formats
        available depend on the backend being used. On Unix systems these
        formats are normally supported:

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
        __init__(self, values, separator=',')

        This saver save data as a text file with the csv format with the given.

        :param values: The values to display
        :type values: AttributesGetter
        :param separator: the separator of two data in the same line
        :type separator: str

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
        """
        save(self, file_name)

        Saves the data in the given file (``file_name``). The format is a text
        file regardless the extension of the file.
        The data is store with the csv format and the header are the data
        returned by :func:`gridsim.iodata.output.AttributesGetter.get_x_unit()`
        and :func:`gridsim.iodata.output.AttributesGetter.get_y_unit()`

        :param file_name: File name (path) where to save the file.
        :type file_name: str
        """

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