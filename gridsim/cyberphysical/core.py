"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.decorators import accepts

class Converter(object):
    def __init__(self, lmin, lmax, ldefault):
        super(Converter, self).__init__()

        self.lmin = lmin
        self.lmax = lmax
        self.ldefault = ldefault

    def call(self,data):
        """

        call(self,data)

        Convert the data before the writing system function

        :param data: data to convert in a writing value
        :return: the converted value
        """
        raise NotImplementedError('Pure abstract method!')

class Aggregator(object):
    def __init__(self):
        super(Aggregator, self).__init__()
    def call(self,datalist):
        """
        call(self,datalist)

        Aggregate all the value passed in datalist and return a single represented value

        :param datalist: list of value to be aggregated
        :return: a single represented value
        """
        raise NotImplementedError('Pure abstract method!')

class Callable(object):
    def __init__(self):
        #fixme
        #super(Callable, self).__init__()
        pass
    def getValue(self,paramtype):
        """
        getValue(self,paramtype)

        This function is called by the simulation each time a new value is required with
        the paramtype id

        :param paramtype: The paramtype associate with the return value
        :return: value that correspond to the paramtype
        """
        raise NotImplementedError('Pure abstract method!')

class WriteParam(object):
    #todo add control type on aggregate and converter
    def __init__(self, paramtype, aggregate, info=None, converter=None):
        super(WriteParam, self).__init__()

        #aggregator function, does the aggregation when datas are received
        self._aggregator = aggregate
        #converter function, does the conversion of the data before writing
        self._converter = converter

        #write paramtype id correspond of the current WriteParam in use
        self.paramtype = paramtype
        self.info = info

        #list of callable to call when the data needs to be updated
        self._callable = []
        #callable respond, datas will be processed with the aggregator function
        self.datalist = []

    @accepts((1, Aggregator))
    def setAggregator(self,aggregator):
        """

        setAggregator(self,aggregator)

        Set the current aggregator function

        :param aggregator: aggregator function
        """

        self._aggregator = aggregator

    @accepts((1, Converter))
    def setConverter(self,converter):

        self._converter = converter

    @accepts((1, Callable))
    def addCallable(self,callable):
        """

        addCallable(self, callable)

        Add Callable to list. This list will be iterate to get new datas

        :param callable: callable to add to the list
        """

        self._callable.append(callable)

    def getWriteParam(self):
        """

        Ask all callable to return the next value. All the values are aggregated
        with the aggregator function

        :return: aggregated value
        """

        self.datalist = []
        for c in self._callable:
            self.datalist.append(c.getValue((self.paramtype,self.info)))
        if self._aggregator == None:
            raise Exception('Aggregate function not defined!')
        else:
            if self._converter == None:
                return self.aggregate(self.datalist)
            else:
                return self.convert(self.aggregate(self.datalist))

    def aggregate(self, datalist):
        """

        aggregate(self, datalist)

        Aggregate the value passed in parameters and return this value

        :param datalist: list of data to aggregate

        :return: output of aggregate value
        """

        return self._aggregator.call(datalist)

    def convert(self, data):

        return self._converter.call(data)

class ParamListener(object):
    def __init__(self):
        #fixme
        #super(ParamListener, self).__init__()
        pass

    def notifyReadParam(self,info,data):
        """

        notifyReadParam(self,paramtype,data)

        notify the listener that a new value from the simulator has been updated

        :param info: paramtype id of the data notified
        :param data: data updated itself
        """
        raise NotImplementedError('Pure abstract method!')

class ReadParam(object):
    def __init__(self, paramtype, info):
        super(ReadParam, self).__init__()

        #registerd listener for the specific paramtype id
        self._listener = []
        #saved data, when data is updated
        self._data = None
        self.info = info
        #the paramtype that listener subscribed on
        self.paramtype = paramtype

    @accepts((1, ParamListener))
    def addListener(self,listener):
        """

        addListener(self,listener)

        Add the listener to the list

        :param listener: listener to add to list
        """
        self._listener.append(listener)

    def pushReadParam(self,data):
        """

        pushReadParam(self,data)

        inform all Listener that a new data has been updated

        :param info: pass some information for the read param
        :param data: updated data published to all listener register in the list
        """
        self._data = data
        for l in self._listener:
            l.notifyReadParam((self.paramtype,self.info),data)
