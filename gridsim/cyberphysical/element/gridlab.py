"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.cyberphysical.core import WriteParam, ReadParam
from gridsim.cyberphysical.external import AbstractCyberPhysicalSystem

from gridsim.cyberphysical.element.aggregator import SumAggregator

from pyModbusTCP.client import ModbusClient
from modbus.modbus import ModBusOverTcp

class GridLabCyberPhysicalSystem(AbstractCyberPhysicalSystem):

    con = {}

    @staticmethod
    def initModbus(host):
        """

        initModbus(host)

        Initialize the connection to the acs800 and sicam host. Check if the connection can be made
        with the two needed connection.

        :param host:
        """
        for c in host:
            if len(c) == 3:
                if c[0] in 'acs800':
                    GridLabCyberPhysicalSystem.con['acs800'] = ModbusClient(host=c[1], port=c[2])  # check the protocol
                    GridLabCyberPhysicalSystem.con['acs800'].open()
                elif c[0] in 'sicam':
                    GridLabCyberPhysicalSystem.con['sicam'] = ModBusOverTcp(c[1], c[2])  # check the protocol
                    if GridLabCyberPhysicalSystem.con['sicam'].open() == False:
                        quit()
        if 'sicam' not in GridLabCyberPhysicalSystem.con or 'acs800' not in GridLabCyberPhysicalSystem.con:
            raise Exception('sicam or acs800 modbus not initialized')

    def __init__(self,friendly_name):
        """

        __init__(self,friendly_name)

        This class communicate using modbus protocol to the asc800 drives and sicam meters

        :param friendly_name: name given to the gridsim Element
        """
        super(GridLabCyberPhysicalSystem, self).__init__(friendly_name)

        #ReadParam list supported
        self.rlist = None
        #WriteParam list supported
        self.wlist = None

        #Technical information to exchange data on modbus
        self._sicamregister = {}
        self._acs800register = {}

        #avoid rewrite same value without a change between
        self._oldwrite = {}

        #Id of the district
        self._slave = 0

    def initialize(self, readparamlist, sicamregister, writeparamlist, acs800register, slave):
        """

        initialize(self, readparamlist, sicamregister, writeparamlist, acs800register, slave)

        Initialize the ReadParam and the WriteParam

        :param readparamlist: readparam list supported
        :param sicamregister: sicam modbus technical information
        :param writeparamlist: writeparam list supported
        :param acs800register: acs800 modbus technical information
        :param slave: salve district id
        """
        self.rlist = readparamlist
        self.wlist = writeparamlist

        self._sicamregister = sicamregister
        self._acs800register = acs800register

        self._slave = slave

        for r in self.rlist:
            self.readparamlist.append(ReadParam(r))
        for w in self.wlist:
            self.writeparamlist.append(WriteParam(w, SumAggregator()))

    def readParams(self):
        """

        readParams(self)

        Read params from the system using modbus over TCP.
        In this case all the data can be read in one time

        :return: read value
        """
        quantity = self._sicamregister['quantity']
        GridLabCyberPhysicalSystem.con['sicam'].send(self._slave,self._sicamregister['all'],quantity*2)# UL1-N,UL2-N,UL3-N,UNE,IL1,IL2,IL3,ILNE
        data = GridLabCyberPhysicalSystem.con['sicam'].receive(1024).encode('hex')

        #TODO check crc

        if len(data) < (6+8*quantity):
            return None
        if data[:6] == '000000':
            return None

        res = []
        for i in range(quantity):
            d = data[6+i*8:6 +(i+1)*8] #get data frame
            res.append(GridLabCyberPhysicalSystem.con['sicam'].measured_value_float_decode(d))

        return res

    def writeParams(self,paramtype,data):
        """

        writeParams(self,paramtype,data)

        Write params to the system using modbus TCP.
        Check if datas are not the same than the last time, and write to the system

        :param paramtype: paramtype id of the data
        :param data: data to write
        """
        if paramtype in self._acs800register.keys():
            # if paramtype not in self._oldwrite.keys():
            #     GridLabCyberPhysicalSystem.con['acs800'].write_multiple_registers(self._acs800register[paramtype],[data])
            #     self._oldwrite[paramtype] = data

            if (paramtype not in self._oldwrite.keys()) or (paramtype in self._oldwrite.keys() and self._oldwrite[paramtype] != data):
                GridLabCyberPhysicalSystem.con['acs800'].write_multiple_registers(self._acs800register[paramtype],[data])
                self._oldwrite[paramtype] = data
