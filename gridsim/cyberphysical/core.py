"""
.. moduleauthor:: Dominique Gabioud <dominique.gabioud@hevs.ch>
.. moduleauthor:: Gillian Basso <gillian.basso@hevs.ch>
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.decorators import accepts, returns


class Converter(object):
    def __init__(self):
        """
        __init__(self)

        Converts the data to an other that is comprehensible by the physical device.
        Check the limit after conversion with de limit data passed in parameters.
        """
        super(Converter, self).__init__()

    @accepts((1, dict))
    @returns(dict)
    def call(self, datadict):
        """
        call(self,datadict)

        Converts the data before the writing system function

        :param datadict: data to convert for the physical device
        :return: the converted value (``dict``)
        """
        raise NotImplementedError('Pure abstract method!')


class Aggregator(object):
    @accepts(((1, 2, 3), (int, float)))
    def __init__(self, limit_min, limit_max, default):
        """
        __init__(self, limit_min, limit_max, default)

        This interface aggregates a list of data passed in parameter.
        Check the limit after aggregation with de limit data passed in parameters.

        :param limit_min: down limit
        :param limit_max: upper limit
        :param default: default value on conversion failure
        """
        super(Aggregator, self).__init__()

        self.limit_min = limit_min
        self.limit_max = limit_max
        self.default = default

    @accepts((1, list))
    @returns((int, float))
    def call(self, datalist):
        """
        call(self,datalist)

        Aggregates all the value passed in datalist and return a single represented value

        :param datalist: list of value to be aggregated
        :return: a single represented value (``list``)
        """
        raise NotImplementedError('Pure abstract method!')


class Callable:
    def __init__(self):
        """
        __init__(self)

        This interface is used to get the value requested by a cyberphysical system on :func:`Callable.get_value`
        function with the ``write_param`` type specified in parameter.

        .. warning:: This interface does not extend ``object`` class. As its implementation should implements
                another class (e.g. :class:`ParamListener`), a
                `diamond problem <https://en.wikipedia.org/wiki/Multiple_inheritance#The_diamond_problem>`_
                could arise.
        """
        pass

    @returns((int, float))
    def get_value(self, write_param):
        """
        get_value(self,write_param)

        This function is called by the simulation each time a new value is required with
        the ``write_param`` id.

        :param write_param: The id of the :class:`WriteParam` associated with the return
            value
        :return: value that correspond to the given :class:`WriteParam`
        """
        raise NotImplementedError('Pure abstract method!')


class WriteParam(object):

    @accepts((3, Aggregator))
    def __init__(self, write_param, info=None, aggregator=None):
        """
        __init__(self, write_param, info=None, aggregator=None)

        It asks its :class:`Callable` to provide data. When all :class:`Callable` retrieve values, data are aggregated
        through :func:`WriteParam.aggregate`.

        :param write_param: single id for the write param
        :param info: full id for the write param, same data passed on :func:`Callable.get_value` function.
        :param aggregator: aggregate function call when
        """
        super(WriteParam, self).__init__()

        # aggregator function does the aggregation when data are received
        self._aggregator = aggregator

        # write param id correspond of the current ParamType in use
        self.write_param = write_param
        self.info = info

        # list of callable to call when the data needs to be updated
        self._callable = []

    @accepts((1, Callable))
    def add_callable(self, callable):
        """
        add_callable(self, callable)

        Adds the given :class:`Callable`.

        :param callable: callable to add to the list
        """
        self._callable.append(callable)

    @returns((int, float))
    def get_value(self):
        """
        get_value(self)

        Asks all :class:`Callable` added to this :class:`WriteParam` to return the next value.
        All the values are aggregated through :func:`Aggregator.call` function.

        :return: aggregated value (int, float)
        """
        datalist = []
        for c in self._callable:
            datalist.append(c.get_value(self.info))
        if self._aggregator is None:
            raise Exception('Aggregate function not defined!')
        else:
            return self._aggregator.call(datalist)

class ParamListener(object):
    def __init__(self):
        """
        __init__(self)

        This interface is used to notify the data read on the cyberphysical system on
        :func:`ParamListener.notify_read_param` function with the :class:`ReadParam` type specified in parameter.

        .. note:: Implementations of this class also usually implement :class:`Callable`.

        .. seealso:: :class:`Callable` for more information.
        """
        super(ParamListener, self).__init__()

    def notify_read_param(self, read_param, data):
        """
        notify_read_param(self,read_param,data)

        Notifies the listener that a new value from the simulator has been updated.

        :param read_param: ParamType id of the data notified
        :param data: data updated itself
        """
        raise NotImplementedError('Pure abstract method!')


class ReadParam(object):
    def __init__(self, read_param, info):
        """
        __init__(self, read_param, info)

        This class holds the properties of a write param. It asks its :class:`Callable` to provide
        data. When all :class:`Callable` retrieve values, data are aggregated through :func:`WriteParam.aggregate`.

        :param read_param:
        :param info:
        """
        super(ReadParam, self).__init__()

        # registerd listener for the specific ParamType id
        self._listener = []
        # saved data, when data is updated
        self._data = None
        self.info = info
        # the ParamType that listener subscribed on
        self.read_param = read_param

    @accepts((1, ParamListener))
    def add_listener(self, listener):
        """
        add_listener(self,listener)

        Adds the listener.

        :param listener: listener to add to list
        """
        self._listener.append(listener)

    @accepts((1, (int, float)))
    def notify_read_param(self, data):
        """
        notify_read_param(self,data)

        Informs all :class:`ParamListener` that a new data has been updated.

        :param data: updated data published to all listener register in the list
        """
        self._data = data
        for l in self._listener:
            l.notify_read_param(self.info, data)
