"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.decorators import accepts, returns


class Converter(object):
    def __init__(self):
        """
        __init__(self,limit_min,limit_max,default)

        Convert the data to an other that is comprehensible by the physical device.
        Check the limit after conversion with de limit data passed in parameters.

        :param limit_min: down limit
        :param limit_max: upper limit
        :param default: default value on conversion fail
        """
        super(Converter, self).__init__()

    @accepts((1, (dict)))
    @returns((dict))
    def call(self, datas):
        """
        call(self,datas)

        Convert the data before the writing system function

        :param datas: datas to convert for the physical device
        :return: the converted value
        """
        raise NotImplementedError('Pure abstract method!')


class Aggregator(object):
    @accepts(((1, 2, 3), (int, float)))
    def __init__(self, limit_min, limit_max, default):
        """
        __init__(self)

        This interface aggregate a list of data passed in parameter. This interface must
        be implemented see SumAggregator class
        Check the limit after aggregation with de limit data passed in parameters.

        :param limit_min: down limit
        :param limit_max: upper limit
        :param default: default value on conversion fail
        """
        super(Aggregator, self).__init__()

        self.limit_min = limit_min
        self.limit_max = limit_max
        self.default = default

    @accepts((1, list))
    @returns((int, float))
    def call(self, datas):
        """
        call(self,datas)

        Aggregate all the value passed in datas and return a single represented value

        :param datas: list of value to be aggregated
        :return: a single represented value
        """
        raise NotImplementedError('Pure abstract method!')


class Callable():
    def __init__(self):
        """
        __init__(self)

        This interface is used to get the value requested by the cyber-physical system on get_value function
        with the write_param type specified in parameter
        """
        pass

    @returns((int, float))
    def get_value(self, write_param):
        """
        get_value(self,write_param)

        This function is called by the simulation each time a new value is required with
        the write_param id

        :param write_param: The write_param associate with the return value
        :return: value that correspond to the write_param
        """
        raise NotImplementedError('Pure abstract method!')


class WriteParam(object):
    @accepts((3, Aggregator))
    def __init__(self, write_param, info=None, aggregate=None):
        """
         __init__(self,write_param,info,aggregate)

        This class hold the properties of a write param. It asks for actors to provide
        a data by the Callable interface. When all actors got values, datas are aggregate by the
        aggregation function.

        :param write_param: single id for the write param
        :param info: full id for the write param, same data passed on get_value function from Callable interface
        :param aggregate: aggregate function call when
        """
        super(WriteParam, self).__init__()

        # aggregator function does the aggregation when datas are received
        self._aggregator = aggregate

        # write paramtype id correspond of the current WriteParam in use
        self.write_param = write_param
        self.info = info

        # list of callable to call when the data needs to be updated
        self._callable = []
        # callable respond, datas will be processed with the aggregator function
        self.datalist = []

    @accepts((1, Callable))
    def add_callable(self, callable):
        """
        add_callable(self, callable)

        Add Callable to list. This list will be iterate to get new datas

        :param callable: callable to add to the list
        """
        self._callable.append(callable)

    @returns((int, float))
    def get_value(self):
        """
        get_value(self)

        Ask all callable to return the next value. All the values are aggregated
        with the aggregator function

        :return: aggregated value
        """
        self.datalist = []
        for c in self._callable:
            self.datalist.append(c.get_value(self.info))
        if self._aggregator is None:
            raise Exception('Aggregate function not defined!')
        else:
            return self.aggregate(self.datalist)

    def aggregate(self, datas):
        """
        aggregate(self, datas)

        Aggregate the value passed in parameters and return this value

        :param datas: list of data to aggregate

        :return: output of aggregate value
        """
        return self._aggregator.call(datas)


class ParamListener(object):
    def __init__(self):
        """
        __init__(self)

        This interface is used to notify the data read on the cyber-physical system on notify_read_param function
        with the read_param type specified in parameter
        """
        super(ParamListener, self).__init__()

    def notify_read_param(self, read_param, data):
        """
        notify_read_param(self,read_param,data)

        Notify the listener that a new value from the simulator has been updated

        :param read_param: paramtype id of the data notified
        :param data: data updated itself
        """
        raise NotImplementedError('Pure abstract method!')


class ReadParam(object):
    def __init__(self, read_param, info):
        super(ReadParam, self).__init__()

        # registerd listener for the specific paramtype id
        self._listener = []
        # saved data, when data is updated
        self._data = None
        self.info = info
        # the paramtype that listener subscribed on
        self.read_param = read_param

    @accepts((1, ParamListener))
    def add_listener(self, listener):
        """
        add_listener(self,listener)

        Add the listener to the list

        :param listener: listener to add to list
        """
        self._listener.append(listener)

    @accepts((1, (int, float)))
    def notify_read_param(self, data):
        """
        notify_read_param(self,data)

        Inform all Listener that a new data has been updated

        :param info: pass some information for the read param
        :param data: updated data published to all listener register in the list
        """
        self._data = data
        for l in self._listener:
            l.notify_read_param(self.info, data)
