from gridsim.cyberphysical.core import WriteParam, ReadParam
from gridsim.cyberphysical.external import AbstractCyberPhysicalSystem

from gridsim.cyberphysical.element.aggregator import SumAggregator

from pyModbusTCP.client import ModbusClient
from gridsim.cyberphysical.physicalsystem.modbus import ModBusOverTcp

class GridLabCyberPhysicalSystem(AbstractCyberPhysicalSystem):
    def __init__(self,friendly_name):
        super(GridLabCyberPhysicalSystem, self).__init__(friendly_name)

        self.rlist = None
        self.wlist = None

        self.con = {}

    def initialize(self, readparamlist, writeparamlist, host):
        self.rlist = readparamlist
        self.wlist = writeparamlist

        # for c in self.host:
        #     if len(c) == 4:
        #         if c[0] in 'acs800':
        #             self.con[c[0]] = ModbusClient(host=c[1], port=c[2])  # check the protocol
        #         elif c[0] in 'sicam':
        #             self.con[c[0]] = ModBusOverTcp(c[1], c[2])  # check the protocol
        # if 'sicam' not in self.con or 'acs800' not in self.con:
        #     raise Exception('sicam or acs800 modbus not initialized')

        for r in self.rlist:
            self.readparamlist.append(ReadParam(r))
        for w in self.wlist:
            self.writeparamlist.append(WriteParam(w, SumAggregator()))

    def readParams(self):
        return [10,20,30,40,50,60]
    def writeParams(self,paramtype,data):
        print('writeparams ' + str(paramtype) + ' ' + str(data))

