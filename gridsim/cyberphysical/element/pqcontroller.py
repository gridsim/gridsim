from gridsim.cyberphysical.external import Actor

import threading

from enum import Enum
import msvcrt

class ParamType(Enum):
    U1 = 1
    U2 = 2
    U3 = 3
    UN = 4
    I1 = 5
    I2 = 6
    I3 = 7
    IN = 8
    UL12 = 9
    UL23 = 10
    UL31 = 11
    USUM = 12
    ISUM = 13
    PL1 = 14
    PL2 = 15
    PL3 = 16
    PA = 17
    QL1 = 18
    QL2 = 19
    QL3 = 20
    QA = 21
    SL1 = 22
    SL2 = 23
    SL3 = 24
    SA = 25
    P = 26
    Q = 27

    @staticmethod
    def getQuantity():
        return 25

class _TerminalListener(object):
    def __init__(self, pqcontroller):
        super(_TerminalListener, self).__init__()

        self.pqcontroller = pqcontroller
        self.temp = ''
        self.c = ''

    def start(self):
        while True:
            if msvcrt.kbhit():
                self.c = msvcrt.getch()
                if self.c == 'e':
                    break
                elif self.c == ' ':
                    if 'p' in self.temp or 'q' in self.temp:
                        if 'p' in self.temp:
                            self.temp = self.temp.replace('p','')
                            self.pqcontroller.changeValueFromTerm(ParamType.P,self.temp)
                        elif 'q' in self.temp:
                            self.temp = self.temp.replace('q', '')
                            self.pqcontroller.changeValueFromTerm(ParamType.Q, self.temp)
                    self.temp = ''
                else:
                    self.temp  = self.temp + self.c
                    print(self.temp)

class PQController(Actor):
    def __init__(self, readparamlist, writeparamlist):
        super(PQController, self).__init__()

        self.readparamtype = readparamlist
        self.writeparamtype = writeparamlist

        self.consoleinputP = 0
        self.consoleinputQ = 1000

        terminal = _TerminalListener(self)
        t = threading.Thread(target=terminal.start)
        t.start()

    def reset(self):
        pass

    def notifyReadParam(self, paramtype, data):
        print('notifyReadParam ' + str(paramtype) + ' ' + str(data))

    def changeValueFromTerm(self, paramtype, value):
        if paramtype == ParamType.P:
            p = int(value) * 4545 / 10000
            if p < 5000:
                self.consoleinputP = p
        elif paramtype == ParamType.Q:
            q = int(value) * 4545 / 10000
            if q < 5000:
                self.consoleinputQ = q

    def getValue(self, paramtype):
        data = self.consoleinputQ
        if paramtype == ParamType.P:
            data = self.consoleinputP
        elif paramtype == ParamType.Q:
            data = self.consoleinputQ
        print('getValue ' + str(paramtype) + ' ' + str(data))
        return data