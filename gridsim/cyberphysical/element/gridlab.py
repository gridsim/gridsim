from gridsim.cyberphysical.core import WriteParam, ReadParam
from gridsim.cyberphysical.external import AbstractCyberPhysicalSystem

from gridsim.cyberphysical.element.aggregator import SumAggregator

from pyModbusTCP.client import ModbusClient
from modbus.modbus import ModBusOverTcp

class GridLabCyberPhysicalSystem(AbstractCyberPhysicalSystem):
    def __init__(self,friendly_name):
        super(GridLabCyberPhysicalSystem, self).__init__(friendly_name)

        self.rlist = None
        self.wlist = None

        self.con = {}

        self._sicamregister = {}
        self._acs800register = {}

        self._slave = 0

    def initialize(self, readparamlist, sicamregister, writeparamlist, acs800register, host, slave):

        self.rlist = readparamlist
        self.wlist = writeparamlist

        self._sicamregister = sicamregister
        self._acs800register = acs800register

        self._slave = slave

        for c in host:
            if len(c) == 3:
                if c[0] in 'acs800':
                    self.con['acs800'] = ModbusClient(host=c[1], port=c[2])  # check the protocol
                    self.con['acs800'].open()
                elif c[0] in 'sicam':
                    self.con['sicam'] = ModBusOverTcp(c[1], c[2])  # check the protocol
                    self.con['sicam'].open()
        if 'sicam' not in self.con or 'acs800' not in self.con:
            raise Exception('sicam or acs800 modbus not initialized')

        for r in self.rlist:
            self.readparamlist.append(ReadParam(r))
        for w in self.wlist:
            self.writeparamlist.append(WriteParam(w, SumAggregator()))

    def readParams(self):
        quantity = self._sicamregister['quantity']
        self.con['sicam'].send(self._slave,self._sicamregister['all'],quantity*2)# UL1-N,UL2-N,UL3-N,UNE,IL1,IL2,IL3,ILNE
        data = self.con['sicam'].receive(1024).encode('hex')

        #check crc

        if len(data) < (6+8*quantity):
            return None
        if data[:6] == '000000':
            return None

        res = []
        for i in range(quantity):
            d = data[6+i*8:6 +(i+1)*8] #get data frame
            res.append(self.con['sicam'].measured_value_float_decode(d))

        return res

    def writeParams(self,paramtype,data):
        if paramtype in self._acs800register.keys():
            #print 'send', paramtype, data
            self.con['acs800'].write_multiple_registers(self._acs800register[paramtype],[data])
