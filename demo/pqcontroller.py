"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.cyberphysical.element import AbstractCyberPhysicalSystem, Actor
from gridsim.cyberphysical.simulation import CyberPhysicalModuleListener

from gridsim.cyberphysical.core import WriteParam, ReadParam

from gridsim.cyberphysical.simulation import CyberPhysicalModule
from gridsim.execution import RealTimeExecutionManager
from gridsim.simulation import Simulator
from gridsim.unit import units

from gridsim.decorators import accepts, returns

from enum import Enum
import threading
import random


class ParamType(Enum):
    WRITEPARAM1 = 0
    WRITEPARAM2 = 1

    READPARAM1 = 2
    READPARAM2 = 3
    READPARAM3 = 4


class TerminalListener(object):
    def __init__(self):
        """
        __init__(self)

        listener for the terminal object
        """
        super(TerminalListener, self).__init__()

    @accepts(2, (int, float))
    def new_terminal_data(self, code, value):
        """
        new_terminal_data(self,code,value)

        This function is called by the terminal listener when new data are available

        :param code: code id of the data
        :param value: new data entered by the user on the console
        """
        raise NotImplementedError('Pure abstract method!')

    def terminal_end(self):
        """
        terminal_data(self)

        This function inform the listener that an exit key is pressed for the terminal thread
        """
        raise NotImplementedError('Pure abstract method!')


class Terminal(object):
    @accepts((1, dict))
    def __init__(self, opcode):
        """
        __init__(self,opcode)

        Listen on the console to grab input from the user and inform back the PQController

        :param opcode: interpretation of the input data
        """
        super(Terminal, self).__init__()

        # current string updated
        self._temp = ''

        # code to identify the ParamType
        if len(opcode) is 0:
            raise Exception('Empty opcode dict provided')
        self._opcode = opcode
        self._opcodelen = len(opcode.keys()[0])

        # abort the listening
        self._abort = False

        # TerminalListener
        self._listener = []

    @accepts((1, TerminalListener))
    def add_listener(self, pq_controller):
        """
        add_listener(self,pq_controller)

        :param pq_controller: controller to be notified on new data coming from the terminal
        """
        if isinstance(pq_controller, TerminalListener):
            self._listener.append(pq_controller)

    def abort(self):
        """
        abort(self)

        Abort the listening on the keyboard
        """
        self._abort = True

    def start(self):
        """
        start(self)

        Listen on the keyboard and inform back the pq_controller listener when new data are entered.
        EX: 5000a1p [SPACE] means 5000 active power (p) of the first district (1) on the first house (A)
        """
        while not self._abort:
            self._temp = raw_input()
            if 'q' in self._temp:
                for l in self._listener:
                    l.terminal_end()
                exit()
            if len(self._temp) > self._opcodelen:
                # get value and code (id of the value)
                s_value = self._temp[:len(self._temp) - self._opcodelen]
                code = self._temp[len(self._temp) - self._opcodelen:]

                try:
                    value = float(s_value)
                    if code in self._opcode.keys():
                        attr = self._opcode[code]
                        # send data to all listeners
                        for l in self._listener:
                            l.new_terminal_data(attr, value)
                except TypeError:
                    print 'Error value inserted'
                except ValueError:
                    print 'Error value inserted'

            self._temp = ''


class PQController(Actor, CyberPhysicalModuleListener, TerminalListener):
    # only one instance of _TerminalListener is available
    terminal = None

    @accepts(((1, 2), list))
    def __init__(self, read_params, write_params):
        """
        __init__(self,read_params,write_params)

        Initialize the PQController Actor with the read param and write param dependency list.

        :param read_params: Read param to register on
        :param write_params: Write param to register on
        """
        super(PQController, self).__init__()

        self.read_params = read_params
        self.write_params = write_params

        self._console_inputs = {}

        self._kill = False

    @accepts((1, dict))
    def init_console(self, opcode):
        """
        initConsole(self)

        Initialize the terminal listener with a thread
        """
        if PQController.terminal is None:
            PQController.terminal = Terminal(opcode)
            t = threading.Thread(target=PQController.terminal.start)
            t.start()
        PQController.terminal.add_listener(self)

    def new_terminal_data(self, code, value):
        self._console_inputs[code] = value
        print 'new_terminal_data', code, value

    def terminal_end(self):
        self._kill = True
        print('exiting program in progress,...')

    @accepts((2, (int, float)))
    def notify_read_param(self, read_param, data):
        if self._kill:
            exit()
        else:
            print 'notify_read_param', str(read_param), str(data)

    @returns((int, float))
    def get_value(self, write_param):
        if self._kill:
            exit()
        elif write_param in self._console_inputs.keys():
            print 'get_value', write_param, self._console_inputs[write_param]
            return self._console_inputs[write_param]
        return 0

    def cyberphysical_module_end(self):
        if PQController.terminal is not None:
            PQController.terminal.abort()


class ConsoleCyberPhysicalSystem(AbstractCyberPhysicalSystem):
    def __init__(self, friendly_name):
        super(ConsoleCyberPhysicalSystem, self).__init__(friendly_name)

    def initialize(self, read_params, write_params):
        for r in read_params:
            self.read_params.append(ReadParam(r, r))
        for w in write_params:
            self.write_params.append(WriteParam(w, w))

    def physical_read_params(self):
        l = []
        for i in range(3):
            l.append(random.uniform(0, 1000))
        return l

    def physical_write_params(self, write_params):
        pass


if __name__ == '__main__':
    readparam = [(ParamType.READPARAM1), (ParamType.READPARAM2), (ParamType.READPARAM3)]
    writeparam = [(ParamType.WRITEPARAM1), (ParamType.WRITEPARAM2)]

    pqcontroller = PQController(readparam, writeparam)

    opcode = {'w1': (ParamType.WRITEPARAM1), 'w2': (ParamType.WRITEPARAM2)}

    pqcontroller.init_console(opcode)

    console = ConsoleCyberPhysicalSystem("consolecyberphysicalsystem")

    console.initialize(readparam, writeparam)
    console.add(pqcontroller)

    Simulator.register_simulation_module(CyberPhysicalModule)

    sim = Simulator(RealTimeExecutionManager(10 * units.seconds))

    sim.cyberphysical.add_actor_listener(console)
    sim.cyberphysical.add_module_listener(pqcontroller)

    sim.reset()
    print('start simulation')
    sim.run(10 * units.seconds, 1 * units.seconds)
    print('end simulation')
