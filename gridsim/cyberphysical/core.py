"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.decorators import accepts

class Aggregator(object):
    def __init__(self):
        super(Aggregator, self).__init__()
    def call(self,unitlist):
        """
        call(self,unitlist)

        Aggregate all the value passed in unitlist and return a single represented value

        :param unitlist: list of value to be aggregated
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
    def __init__(self, paramtype, aggregate):
        super(WriteParam, self).__init__()

        #aggregator function, does the aggregation when datas are received
        self._aggregator = aggregate
        #write paramtype id correspond of the current WriteParam in use
        self.paramtype = paramtype

        #list of callable to call when the data needs to be updated
        self._callable = []
        #callable respond, datas will be processed with the aggregator function
        self.unitlist = []

    @accepts((1,Aggregator))
    def setAggregator(self,aggregator):
        """

        setAggregator(self,aggregator)

        Set the current aggregator function

        :param aggregator: aggregator function
        """

        self._aggregator = aggregator

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

        self.unitlist = []
        for c in self._callable:
            self.unitlist.append(c.getValue(self.paramtype))
        if self.aggregate == None:
            raise NotImplementedError('Aggregate function not defined!')
        else:
            return self.aggregate(self.unitlist)

    def aggregate(self, unitlist):
        """

        aggregate(self, unitlist)

        Aggregate the value passed in parameters and return this value

        :param unitlist: list of data to aggregate

        :return: output of aggregate value
        """

        return self._aggregator.call(unitlist)

    def reset(self):
        """

        reset(self)

        Reset the WriteParam object
        """

        self.unitlist = []
        #self._callable = []

class ParamListener(object):
    def __init__(self):
        #fixme
        #super(ParamListener, self).__init__()
        pass

    def notifyReadParam(self,paramtype,data):
        """

        notifyReadParam(self,paramtype,data)

        notify the listener that a new value from the simulator has been updated

        :param paramtype: paramtype id of the data notified
        :param data: data updated itself
        """

        raise NotImplementedError('Pure abstract method!')

class ReadParam(object):
    def __init__(self, paramtype):
        super(ReadParam, self).__init__()

        #registerd listener for the specific paramtype id
        self._listener = []
        #saved data, when data is updated
        self.data = None
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

        pushReadParam(self,unit)

        inform all Listener that a new data has been updated

        :param data: updated data published to all listener register in the list
        """

        self.data = data
        for l in self._listener:
            l.notifyReadParam(self.paramtype,self.data)
