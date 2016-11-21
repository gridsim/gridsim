"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.cyberphysical.external import Actor
from gridsim.cyberphysical.simulation import CyberPhysicalModuleListener

import threading

import msvcrt

class _TerminalListener(object):
    def __init__(self, pqcontroller,opcode):
        """

        __init__(self,pqcontroller)

        Listen on the console to grab input from the user and inform back the PQController

        :param pqcontroller: callback to pqcontroller when new data are entered by the user
        """
        super(_TerminalListener, self).__init__()

        #callback object
        self._pqcontroller = pqcontroller
        #current string updated
        self._temp = ''
        #new char entered by the user
        self._c = ''

        #code to identify the ParamType
        self._opcode = opcode

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
        EX: 5000a1p [SPACE] means 5000 active power (p) of the first district (1) on the first house (A)
        """
        while not self._abort:
            if msvcrt.kbhit():
                self._c = msvcrt.getch()
                if self._c == 'e':
                    break
                elif self._c == ' ':
                    if ('a' in self._temp or 'b' in self._temp or 'c' in self._temp or 'd' in self._temp) and \
                            ('p' in self._temp or 'q' in self._temp) and \
                            ('1' in self._temp or '2' in self._temp or '3' in self._temp):
                        print 'enter'
                        if len(self._temp) > 3:
                            value = self._temp[:len(self._temp)-3]
                            code = self._temp[len(self._temp)-3:]

                            print value, code

                            if code in self._opcode.keys():
                                attr = self._opcode[code]
                                attr = str(attr[0]) + str(attr[1]) + str(attr[2])
                                self._pqcontroller.changeValueFromTerm(attr, value)
                    self._temp = ''
                else:
                    self._temp  = self._temp + self._c
                    print(self._temp)

class PQController(Actor,CyberPhysicalModuleListener):

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

        self._consoleinput = {}

    def initConsole(self,opcode):
        """

        initConsole(self)

        Initialize the terminal listener with a thread
        """
        PQController.terminal = _TerminalListener(self,opcode)
        t = threading.Thread(target=PQController.terminal.start)
        t.start()

    def init(self):
        pass

    def notifyReadParam(self, info, data):
        """

        notifyReadParam(self,paramtype,data)

        Get new data from the simulation

        :param paramtype: paramtype of data updated
        :param data: data updated
        """
        print 'notifyReadParam', str(info), str(data)

    def changeValueFromTerm(self, code, value):
        """

        changeValueFromTerm(self,paramtype,value)

        This function is called by the terminal listener when new data are available

        :param paramtype: paramtype id of the data
        :param value: new data entered by the user on the console
        """
        self._consoleinput[code] = value
        print code, value

    def getValue(self, info):
        """

        getValue(self,paramtype)

        Return the value corresponding to the paramtype given in parameter

        :param paramtype: paramtype of the returned value
        :return: compensate user's value entered on the keyboard
        """
        if len(info) == 2:
            attr = str(info[0]) + str(info[1][0]) + str(info[1][1])
        else:
            return 0

        if attr in self._consoleinput.keys():
            #print('getValue ' + str(attr) + ' ' + str(self._consoleinput[attr]))
            return self._consoleinput[attr]
        return 0

    def cyberphysicalModuleEnd(self):
        """

        cyberphysicalModuleEnd(self)

        Terminate the terminal listening
        """
        if PQController.terminal != None:
            PQController.terminal.abort()
