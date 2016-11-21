"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.core import AbstractSimulationElement
from gridsim.cyberphysical.core import Callable, ParamListener

from gridsim.decorators import accepts

class Actor(Callable, ParamListener):
    def __init__(self):
        """
        __init__(self)

        Actor are from the AbstractCyberPhysicalSystem ask for given a value corresponding to the ParamType that
        it register on. The actor is informed by the ACPS when new data are updated
        """
        super(Actor, self).__init__()

        #list of write ParamType to register on
        self.writeparamtype = []
        #list of read ParamType to register on
        self.readparamtype = []

    def init(self):
        """

        init(self)

        Initialize the Actor

        """
        raise NotImplementedError('Pure abstract method!')

    def getListWriteParam(self):
        """

        getListWriteParam(self)

        Return the list of write ParamType to register on. The actor will be asked for providing the
        value of the given ParamType on running simulation time

        :return: write ParamType to register on
        """
        return self.writeparamtype

    def getListReadParam(self):
        """

        getListReadParam(self)

        Return the list of Read ParamType to register on. The actor will be inform of new values updated
        in the simulation

        :return: read ParamType to register on
        """
        return self.readparamtype

class AbstractCyberPhysicalSystem(AbstractSimulationElement):
    def __init__(self,friendly_name):
        """

        __init__(self,friendly_name)

        AbstractCyberPhysicalSystem class create ReadParam and WriteParam that Actors can register on.

        :param friendly_name:
        """
        super(AbstractCyberPhysicalSystem, self).__init__(friendly_name)

        #list of actor added to the system
        self.actors = []
        #list of WriteParam instance created
        self.writeparamlist = []
        #list of ReadParam instance created
        self.readparamlist = []

    @accepts((1,Actor))
    def add(self, actor):
        """

        add(self, actor)

        add a single actor to the system and register it with the ReadParam and WriteParam
        that it want to listen and be callable on

        :param actor: actor to register in the system
        :return:  same actor, with id
        """
        rparamlist = actor.getListReadParam()
        wparamlist = actor.getListWriteParam()

        #subscribe actors when the cyberphysicalsystem support the paramtype on write
        for w in self.writeparamlist:
            for a in wparamlist:
                if a == w.paramtype:
                    w.addCallable(actor)
        # subscribe actors when the cyberphysicalsystem support the paramtype on read
        for r in self.readparamlist:
            for a in rparamlist:
                if a == r.paramtype:
                    r.addListener(actor)

        actor.id = len(self.actors)
        self.actors.append(actor)
        return actor

    def readParams(self):
        """

        readParams(self)

        read the data on the system

        :return: read data
        """
        raise NotImplementedError('Pure abstract method!')

    def writeParams(self,paramtype,data):
        """

        writeParams(self,paramtype,data)

        write the data to the system

        :param paramtype: paramtype id of the data to write
        :param data: data to write
        """
        raise NotImplementedError('Pure abstract method!')

    def reset(self):
        """

        reset(self)

        Reset and Initialize all actors registered
        """
        #fixme all the actors are called from each cyberphysicalsystem they register on
        #for a in self.actors:
        #    a.init()
        pass


    def calculate(self, time, delta_time):
        """

        calculate(self,time,dela_time)

        Read all ReadParam on the system and inform the updated values to all Actors
        """
        read = self.readParams() #give it in the right order
        if read != None:
            for r in self.readparamlist:
                #check the len of the read data and compare to the readparamlist
                if len(read) != 0:
                    r.pushReadParam(read.pop(0))
                else:
                    raise Exception('Missing data from physical device to read - not enough data compare to the readparamlist given')
                    #break

    def update(self, time, delta_time):
        """

        update(self,time,delta_time)

        Get aggregated values from Actors and write them on the system
        """
        for w in self.writeparamlist:
            self.writeParams(w.paramtype, w.getWriteParam())
