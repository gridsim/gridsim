"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.core import AbstractSimulationElement
from gridsim.cyberphysical.core import Callable, ParamListener, Converter


from gridsim.decorators import accepts, returns
import types

class Actor(Callable, ParamListener):
    def __init__(self):
        """
        __init__(self)

        Actor are from the AbstractCyberPhysicalSystem ask for given a value corresponding to the ParamType that
        it register on. The actor is informed by the ACPS when new data are updated
        """
        super(Actor, self).__init__()

        # list of write ParamType to register on
        self.write_params = []
        # list of read ParamType to register on
        self.read_params = []

    def init(self):
        """
        init(self)

        Initialize the Actor
        """
        raise NotImplementedError('Pure abstract method!')

    @returns((list))
    def get_write_params(self):
        """
        getListWriteParam(self)

        Return the list of write ParamType to register on. The actor will be asked for providing the
        value of the given ParamType on running simulation time

        :return: write ParamType to register on
        """
        return self.write_params

    @returns((list))
    def get_read_params(self):
        """
        get_read_params(self)

        Return the list of Read ParamType to register on. The actor will be inform of new values updated
        in the simulation

        :return: read ParamType to register on
        """
        return self.read_params


class AbstractCyberPhysicalSystem(AbstractSimulationElement):
    @accepts((1,str),(2,(dict,types.NoneType)))
    def __init__(self, friendly_name, converters=None):
        """
        __init__(self,friendly_name)

        AbstractCyberPhysicalSystem class create ReadParam and WriteParam that Actors can register on.

        :param friendly_name: give a friendly name for the element in the simulation
        :param converters: list of converter function for the write params
        """
        super(AbstractCyberPhysicalSystem, self).__init__(friendly_name)

        # list of actor added to the system
        self.actors = []
        # list of WriteParam instance created
        self.write_params = []
        # list of ReadParam instance created
        self.read_params = []

        self.converters = converters

    @accepts((1, Actor))
    @returns((Actor))
    def add(self, actor):
        """
        add(self, actor)

        add a single actor to the system and register it with the ReadParam and WriteParam
        that it want to listen and be callable on

        :param actor: actor to register in the system
        :return:  same actor, with id
        """
        actor_read_params = actor.get_read_params()
        actor_write_params = actor.get_write_params()

        # subscribe actors when the cyberphysicalsystem support the paramtype on write
        for w in self.write_params:
            for a in actor_write_params:
                if a is w.paramtype:
                    w.add_callable(actor)
        # subscribe actors when the cyberphysicalsystem support the paramtype on read
        for r in self.read_params:
            for a in actor_read_params:
                if a is r.paramtype:
                    r.add_listener(actor)

        actor.id = len(self.actors)
        self.actors.append(actor)
        return actor

    def physical_read_params(self):
        """
        physical_read_params(self)

        read the data on the system

        :return: read data
        """
        raise NotImplementedError('Pure abstract method!')

    @accepts((2, (dict, types.NoneType)))
    def physical_converter_params(self, write_params):
        """
        physical_converter_params(self,write_params)

        :param write_params: list of data to convert
        :return: list of data converted
        """
        if self.converters is None:
            return write_params

        for write_param,value in write_params.items():
            if write_param in self.converters.keys():
                converter = self.converters[write_param]
                #TODO check instance with exception
                write_params[write_param] = converter.call(value)

        return write_params

    def physical_write_params(self, write_params):
        """
        physical_write_params(self,write_params)

        write the data to the system

        :param write_params: map of {id:datas} to write to the cyberphysical system
        """
        raise NotImplementedError('Pure abstract method!')

    def reset(self):
        pass

    def calculate(self, time, delta_time):
        """
        calculate(self,time,dela_time)

        Read all ReadParam on the system and inform the updated values to all Actors
        """
        read = self.physical_read_params()  # give it in the right order
        if read is not None:
            for r in self.read_params:
                # check the len of the read data and compare to the read params
                if len(read) is not 0:
                    r.notify_read_param(read.pop(0))
                else:
                    raise Exception('Missing data from physical device to read -'
                                    ' not enough data compare to the read params given')

    def update(self, time, delta_time):
        """
        update(self,time,delta_time)

        Get aggregated values from Actors and write them on the system
        """
        if len(self.write_params) is 0:
            return

        write_params = {}
        for w in self.write_params:
            write_params[w.write_param] = w.get_value()
        self.physical_converter_params(write_params)
        self.physical_write_params(write_params)
