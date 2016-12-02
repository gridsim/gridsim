"""
.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.core import AbstractSimulationElement
from gridsim.cyberphysical.core import Callable, ParamListener

from gridsim.decorators import accepts, returns

import types


class Actor(Callable, ParamListener):

    def __init__(self):
        """
        __init__(self)

        An actor represents a (set of) virtual device. Therefore it has to communicate with a real device to send energy
        to a real network. To do so, it has to be connected to :class:`gridsim.cyberphysical.core.ReadParam` to receive
        data from real device and connected to :class:`gridsim.cyberphysical.core.WriteParam` to influence a device.
        This is done by a registration to an :class:`AbstractCyberPhysicalSystem`. This registration also adds the
        :class:`Actor` to the simulation.

        .. note:: More details about :class:`Actor` can be found at :ref:`gridsim-actor`.
        """
        super(Actor, self).__init__()

        # list of write ParamType to register on
        self.write_params = []
        # list of read ParamType to register on
        self.read_params = []

    def notify_read_param(self, read_param, data):
        """
        notify_read_param(self,read_param,data)

        Notifies the listener that a new value from the simulator has been updated.

        :param read_param: paramtype id of the data notified
        :param data: data updated itself
        """
        super(Actor, self).notify_read_param(read_param, data)

    def get_value(self, write_param):
        """
        get_value(self,write_param)

        This function is called by the simulation each time a new value is required with
        the ``write_param`` id.

        :param write_param: The id of the :class:`gridsim.cyberphysical.core.WriteParam` associated with the return
            value
        :return: value that correspond to the given :class:`gridsim.cyberphysical.core.WriteParam`
        """
        super(Actor, self).get_value(self, write_param)


class AbstractCyberPhysicalSystem(AbstractSimulationElement):

    @accepts((1, str), (2, (dict, types.NoneType)))
    def __init__(self, friendly_name, converters=None):
        """
        __init__(self,friendly_name)

        An :class:`AbstractCyberPhysicalSystem` creates ReadParam and WriteParam to communicate with real devices.
        Actors can be registered to an :class:`AbstractCyberPhysicalSystem` to influence the real device the
        :class:`AbstractCyberPhysicalSystem` is connected.

        :param friendly_name: give a friendly name for the element in the simulation
        :param converters: Dict of Converter function for the write params
        """
        super(AbstractCyberPhysicalSystem, self).__init__(friendly_name)

        # list of actor added to the system
        self.actors = []
        # list of WriteParam instance created
        self.write_params = []
        # list of ReadParam instance created
        self.read_params = []

        # this is the converter object for the physical device
        self.converters = converters

        # mutex for the feedback control
        # self.mutex = Lock()

    @accepts((1, Actor))
    @returns(Actor)
    def add(self, actor):
        """
        add(self, actor)

        Adds an actor to the system and register it with the ReadParam and WriteParam
        that it wants to be connected.

        :param actor: :class:`Actor` to register in the system
        :return: the :class:`Actor`
        """
        actor_read_params = actor.read_params
        actor_write_params = actor.write_params

        # subscribe actors when the cyberphysicalsystem support the paramtype on write
        for w in self.write_params:
            for a in actor_write_params:
                if a is w.write_param:
                    w.add_callable(actor)
        # subscribe actors when the cyberphysicalsystem support the paramtype on read
        for r in self.read_params:
            for a in actor_read_params:
                if a is r.read_param:
                    r.add_listener(actor)

        actor.id = len(self.actors)
        self.actors.append(actor)
        return actor

    # fixme regulation manager
    # @returns((int, float))
    # def physical_read_regulation(self, write_param):
    #     """
    #     physical_read_regulation(self, write_param):
    #
    #     This is the measure value for regulator
    #
    #     :return: read value from physical device
    #     """
    #     raise NotImplementedError('Pure abstract method!')

    def physical_read_params(self):
        """
        physical_read_params(self)

        Reads the data on the system.

        :return: read data list
        """
        raise NotImplementedError('Pure abstract method!')

    @accepts((2, (dict, types.NoneType)))
    @returns(dict)
    def physical_converter_params(self, write_params):
        """
        physical_converter_params(self,write_params)

        :param write_params: list of data to convert
        :return: list of data converted
        """
        if self.converters is None:
            return write_params

        for write_param, value in write_params.items():
            if write_param in self.converters.keys():
                converter = self.converters[write_param]
                # TODO check instance with exception (subclass)
                write_params[write_param] = converter.call(value)

        return write_params

    # fixme regulation manager
    # def physical_regulation_params(self,write_params):
    #     """
    #     physical_regulation_params(self,write_params)
    #
    #
    #     :param write_params:
    #     :return:
    #     """
    #     raise NotImplementedError('Pure abstract method!')

    def physical_write_params(self, write_params):
        """
        physical_write_params(self,write_params)

        Writes the data to the system.

        :param write_params: map of {id:datas} to write to the cyberphysical system
        """
        raise NotImplementedError('Pure abstract method!')

    # fixme regulation manager
    # def do_regulation(self, write_param, data):
    #     """
    #     do_regulation(self,write_param,data)
    #
    #     :param write_param:
    #     :param data:
    #     :return:
    #     """
    #     self.mutex.acquire()
    #     self.physical_write_params(self.physical_converter_params({write_param:data}))
    #     self.mutex.release()
    #     time.sleep(2)
    #
    #     for i in range(0,3):
    #         self.mutex.acquire()
    #         print write_param, data
    #         error = data - self.physical_read_regulation(write_param)
    #         get_new_params = self.physical_regulation_params({write_param:error})
    #         write_value= self.physical_converter_params({write_param:get_new_params+data})
    #         self.physical_write_params({write_param:write_value})
    #         self.mutex.release()
    #         time.sleep(5)

    def reset(self):
        """
        reset(self)

        Nothing to reset.
        """
        pass

    def calculate(self, t, dt):
        """
        calculate(self,t,dt)

        Reads all :class:`ReadParam` on the system and inform the updated values to all :class:`Actor`.
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

    def update(self, t, dt):
        """
        update(self,time,delta_time)

        Gets aggregated values from :class:`Actor` and write them on the system.
        """
        if len(self.write_params) is 0:
            return

        write_params = {}
        for w in self.write_params:
            write_params[w.write_param] = w.get_value()
        self.physical_converter_params(write_params)
        self.physical_write_params(write_params)

        #fixme regulation feedback control
        # threads = []
        # for w in self.write_params:
        #     thread = threading.Thread(target=self.do_regulation, args = (w.write_param, w.get_value(),))
        #     threads.append(thread)
        #     thread.start()
        #
        # for th in threads:
        #     th.join()
