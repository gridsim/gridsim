"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.cyberphysical.external import Actor

import threading

from enum import Enum
import msvcrt
import struct

class ParamType(Enum):
    """
    ParamType list using in this program to identify the value
    """

    #unit 1
    un1_U1 = 0
    un1_U2 = 1
    un1_U3 = 2
    un1_UN = 3
    un1_I1 = 4
    un1_I2 = 5
    un1_I3 = 6
    un1_IN = 7
    un1_UL12 = 8
    un1_UL23 = 9
    un1_UL31 = 10
    un1_USUM = 11
    un1_ISUM = 12
    un1_PL1 = 13
    un1_PL2 = 14
    un1_PL3 = 15
    un1_PA = 16
    un1_QL1 = 17
    un1_QL2 = 18
    un1_QL3 = 19
    un1_QA = 20
    un1_SL1 = 21
    un1_SL2 = 22
    un1_SL3 = 23
    un1_SA = 24
    un1_P = 25
    un1_Q = 26

    #unit 2
    un2_U1 = 27
    un2_U2 = 28
    un2_U3 = 29
    un2_UN = 30
    un2_I1 = 31
    un2_I2 = 32
    un2_I3 = 33
    un2_IN = 34
    un2_UL12 = 35
    un2_UL23 = 36
    un2_UL31 = 37
    un2_USUM = 38
    un2_ISUM = 39
    un2_PL1 = 40
    un2_PL2 = 41
    un2_PL3 = 42
    un2_PA = 43
    un2_QL1 = 44
    un2_QL2 = 45
    un2_QL3 = 46
    un2_QA = 47
    un2_SL1 = 48
    un2_SL2 = 49
    un2_SL3 = 50
    un2_SA = 51
    un2_P = 52
    un2_Q = 53

    #unit3
    un3_U1 = 54
    un3_U2 = 55
    un3_U3 = 56
    un3_UN = 57
    un3_I1 = 58
    un3_I2 = 59
    un3_I3 = 60
    un3_IN = 61
    un3_UL12 = 62
    un3_UL23 = 63
    un3_UL31 = 64
    un3_USUM = 65
    un3_ISUM = 66
    un3_PL1 = 67
    un3_PL2 = 68
    un3_PL3 = 69
    un3_PA = 70
    un3_QL1 = 71
    un3_QL2 = 72
    un3_QL3 = 73
    un3_QA = 74
    un3_SL1 = 75
    un3_SL2 = 76
    un3_SL3 = 77
    un3_SA = 78
    un3_P = 79
    un3_Q = 80

    @staticmethod
    def getQuantity():
        """

        getQuantity()

        return the number of ReadParam per district

        :return: number of ReadParam per district
        """
        return 25

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
        self.opcode = {}

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
        self.opcode['pa'] = ParamType.un1_P
        self.opcode['qa'] = ParamType.un1_Q
        self.opcode['pb'] = ParamType.un2_P
        self.opcode['qb'] = ParamType.un2_Q
        self.opcode['pc'] = ParamType.un3_P
        self.opcode['qc'] = ParamType.un3_Q

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
                                limit = 0
                                try:
                                    # if 'p' in code :
                                    #     limit = int(value) / 22 * 10
                                    # elif 'q' in code:
                                    #     limit = (int(value) - 1990) * -1 / 2.254
                                    #
                                    # if limit < 10000:
                                    #     val = int(struct.pack('>h', limit).encode('hex'), 16)
                                        self.pqcontroller.changeValueFromTerm(self.opcode[code], value) #val
                                except ValueError:
                                    pass
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

        self._consoleinput = {}

    def initConsole(self):
        """

        initConsole(self)

        Initialize the terminal listener with a thread

        """
        PQController.terminal = _TerminalListener(self)
        t = threading.Thread(target=PQController.terminal.start)
        t.start()

    def init(self):
        """

        init(self)

        Initialize the starting values with default ones

        """
        self._consoleinput[ParamType.un1_P] = 0
        self._consoleinput[ParamType.un1_Q] = 1000

        self._consoleinput[ParamType.un2_P] = 0
        self._consoleinput[ParamType.un2_Q] = 1000

        self._consoleinput[ParamType.un3_P] = 0
        self._consoleinput[ParamType.un3_Q] = 1000

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
            value = 0
            try:
                if ParamType.un1_P == paramtype or ParamType.un2_P == paramtype or ParamType.un3_P == paramtype:
                    value = self._consoleinput[paramtype] / 22 * 10
                elif ParamType.un1_Q == paramtype or ParamType.un2_Q == paramtype or ParamType.un3_Q == paramtype:
                    value = (self._consoleinput[paramtype] - 1990) * -1 / 2.254

                if value < 10000:
                    return int(struct.pack('>h', value).encode('hex'), 16)
            except ValueError:
                pass

    def kill(self,time):
        """

        kill(self,time)

        Terminate the thread when the simulation reaches the end

        :param time: end time
        """
        if PQController.terminal != None:
            PQController.terminal.abort()
