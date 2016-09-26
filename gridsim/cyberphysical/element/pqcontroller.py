from gridsim.decorators import accepts
from gridsim.cyberphysical.core import Actor

import threading

from enum import Enum
import msvcrt

class ParamType(Enum):
    P = 0
    Q = 1
    I = 2
    U = 3

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
        self.consoleinputQ = 0

        terminal = _TerminalListener(self)
        t = threading.Thread(target=terminal.start)
        t.start()

    def reset(self):
        pass

    def notifyReadParam(self, paramtype, data):
        print('notifyReadParam ' + str(paramtype) + ' ' + str(data))

    def changeValueFromTerm(self, paramtype, value):
        if paramtype == ParamType.P:
            self.consoleinputP = int(value)
        elif paramtype == ParamType.Q:
            self.consoleinputQ = int(value)

    def getValue(self, paramtype):
        data = self.consoleinputQ
        if paramtype == ParamType.P:
            data = self.consoleinputP
        elif paramtype == ParamType.Q:
            data = self.consoleinputQ
        print('getValue ' + str(paramtype) + ' ' + str(data))
        return data