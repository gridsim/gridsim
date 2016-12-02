"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.cyberphysical.element import Actor
from gridsim.cyberphysical.simulation import CyberPhysicalModuleListener

from gridsim.decorators import accepts, returns

import threading
import msvcrt


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
        self._opcode = opcode

        # abort the listening
        self._abort = False

        # pqcontroller listener
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
            if msvcrt.kbhit():
                # get char from the terminal
                _c = msvcrt.getch()
                if _c is 'e':
                    break
                elif _c is ' ':
                    if len(self._temp) > 3:
                        # get value and code (id of the value)
                        s_value = self._temp[:len(self._temp) - 3]
                        code = self._temp[len(self._temp) - 3:]

                        try:
                            value = float(s_value)
                            if code in self._opcode.keys():
                                attr = self._opcode[code]
                                # send data to all listeners
                                for l in self._listener:
                                    l.new_terminal_data(attr, value)
                        except TypeError:
                            pass

                    self._temp = ''
                else:
                    self._temp = self._temp + _c


class PQController(Actor, CyberPhysicalModuleListener, TerminalListener):
    # only one instance of _TerminalListener is available
    terminal = None

    @accepts(((1, 2), (list)))
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

    @accepts((1, dict))
    def initConsole(self, opcode):
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

    @accepts((2, (int, float)))
    def notify_read_param(self, read_param, data):
        print 'notify_read_param', str(read_param), str(data)

    @returns((int, float))
    def get_value(self, write_param):
        if write_param in self._console_inputs.keys():
            print 'get_value', write_param, self._console_inputs[write_param]
            return self._console_inputs[write_param]
        return 0

    def cyberphysical_module_end(self):
        if PQController.terminal is not None:
            PQController.terminal.abort()
