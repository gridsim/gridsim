"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.cyberphysical.external import Actor

from paramtype import ParamType

import threading

import msvcrt

class _TerminalListener(object):
    def __init__(self, pqcontroller):
        """

        __init__(self,pqcontroller)

        Listen on the console to grab input from the user and inform back the PQController

        :param pqcontroller: callback to pqcontroller when new data are entered by the user
        """
        super(_TerminalListener, self).__init__()

        #callback object
        self.pqcontroller = pqcontroller
        #current string updated
        self.temp = ''
        #new char entered by the user
        self.c = ''

        #code to identify the ParamType
        self.opcode = {'pa':ParamType.un1_P,'qa':ParamType.un1_Q,
                       'pb':ParamType.un2_Q,'qb':ParamType.un2_Q,
                       'pc':ParamType.un3_Q,'qc':ParamType.un3_Q}

        #abort the listening
        self._abort = False

    def abort(self):
        """

        abort(self)

        Abort the listening on the keyboard

        """
        self._abort = True

    def start(self):
        """

        start(self)

        Listen on the keyboard and inform back the pqcontroller when new data are entered.
        EX: 5000pa [SPACE] means 5000 active power on the first unit (A)

        """
        while not self._abort:
            if msvcrt.kbhit():
                self.c = msvcrt.getch()
                if self.c == 'e':
                    break
                elif self.c == ' ':
                    if ('p' in self.temp or 'q' in self.temp) and ('a' in self.temp or 'b' in self.temp or 'c' in self.temp):
                        print 'enter'
                        if len(self.temp) > 2:
                            value = self.temp[:len(self.temp)-2]
                            code = self.temp[len(self.temp)-2:]

                            print value, code

                            if code in self.opcode.keys():
                                self.pqcontroller.changeValueFromTerm(self.opcode[code], value)
                    self.temp = ''
                else:
                    self.temp  = self.temp + self.c
                    print(self.temp)

class PQController(Actor):

    terminal = None

    def __init__(self, readparamlist, writeparamlist):
        """

        __init__(self,readparamlist,writeparamlist)

        Initialize the PQController Actor with the readparam and writeparam dependency list

        :param readparamlist: Read param to register on
        :param writeparamlist: Write param to regsiter on
        """
        super(PQController, self).__init__()

        self.readparamtype = readparamlist
        self.writeparamtype = writeparamlist

        self._consoleinput = {ParamType.un1_P: 0,ParamType.un1_Q: 1000,
                              ParamType.un2_P: 0, ParamType.un2_Q: 1000,
                              ParamType.un3_P: 0, ParamType.un3_Q: 1000,}

    def initConsole(self):
        """

        initConsole(self)

        Initialize the terminal listener with a thread
        """
        PQController.terminal = _TerminalListener(self)
        t = threading.Thread(target=PQController.terminal.start)
        t.start()

    def init(self):
        pass

    def notifyReadParam(self, paramtype, data):
        """

        notifyReadParam(self,paramtype,data)

        get new data from the simulation

        :param paramtype: paramtype of data updated
        :param data: data updated
        """
        print('notifyReadParam ' + str(paramtype) + ' ' + str(data))

    def changeValueFromTerm(self, paramtype, value):
        """

        changeValueFromTerm(self,paramtype,value)

        This function is called by the terminal listener when new data is available

        :param paramtype: paramtype id of the data
        :param value: new data entered by the user on the console
        """
        self._consoleinput[paramtype] = value
        print paramtype, value

    def getValue(self, paramtype):
        """

        getValue(self,paramtype)

        return the value corresponding to the paramtype given in parameter

        :param paramtype: paramtype of the returned value
        :return: compensate user's value entered on the keyboard
        """
        if paramtype in self._consoleinput.keys():
            print('getValue ' + str(paramtype) + ' ' + str(self._consoleinput[paramtype]))
            return self._consoleinput[paramtype]

    def kill(self,time):
        """

        kill(self,time)

        Terminate the thread when the simulation reaches the end

        :param time: end time
        """
        if PQController.terminal != None:
            PQController.terminal.abort()
