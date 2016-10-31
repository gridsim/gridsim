"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""
from gridsim.cyberphysical.core import WriteParam, ReadParam
from gridsim.cyberphysical.external import AbstractCyberPhysicalSystem

from pyModbusTCP.client import ModbusClient
from modbus.modbus import ModBusOverTcp

from paramtype import ParamType

definedhost = {'a':{'acs800':('153.109.14.46',502),'sicam':('153.109.14.47',502)},
         'b':{'acs800':('153.109.14.51',502),'sicam':('153.109.14.52',502)},
         'c':{'acs800':('153.109.14.56',502),'sicam':('153.109.14.57',502)},
         'd':{'acs800':('153.109.14.61',502),'sicam':('153.109.14.62',502)}}

class DisctrictInitializer(object):

    district = {}

    @staticmethod
    def initializeHost(districtname,host=None):
        """

        initializeHost(districtnams,host)

        Initialize the connection with the gridlab district

        :param districtname: district letter
        :param host: optional, tuple with address and port for the host
        :return: the corresponding socket connection to the house
        """

        if host == None:
            if districtname in definedhost.keys():
                host = definedhost[districtname]
            else:
                raise Exception('No Host found')

        if districtname in DisctrictInitializer.district.keys():
            return DisctrictInitializer.district[districtname]

        con = {}
        for n,h in host.items():
            if len(h) == 2: # need to have address and port
                if n in 'acs800':
                    con['acs800'] = ModbusClient(host=h[0], port=h[1])  # check the protocol
                    if con['acs800'].open() == False:
                        raise Exception('Cannot connect to acs800')
                elif n in 'sicam':
                    con['sicam'] = ModBusOverTcp(host=h[0], port=h[1])  # check the protocol
                    if con['sicam'].open() == False:
                        raise Exception('Cannot connect to sicam')
        if 'sicam' not in con or 'acs800' not in con:
            raise Exception('sicam or acs800 modbus not initialized')

        DisctrictInitializer.district[districtname] = con
        return con

    @staticmethod
    def initializeReadRegisterParam(districtname,housenumber):
        """

        initializeReadRegisterParam(districtname,housename)

        Generic read parameter for the district initializer

        :param districtname: district letter
        :param housename: id of the slave house
        :return: tuple with salve address, register offset with length and ParamType
        """
        slave = 0
        district = ['a', 'b', 'c', 'd']

        register = {'all': 40201, 'quantity': ParamType.getQuantity()}
        paramtype = []

        for i in range((housenumber-1)*27,(housenumber-1)*27+ParamType.getQuantity()):
            paramtype.append(ParamType(i))

        if districtname in district:
            slave = (district.index(districtname)+1)*10+housenumber

        return slave,register,paramtype

    @staticmethod
    def initializeWriteRegisterParam(housenumber):
        """

        initializeWriteRegisterParam(housenumber)

        Generic write parameter for districts initializer

        :param housenumber: id of the house
        :return: register offset with corresponding writeparam
        """
        register = {}
        if housenumber == 1:
            register = {ParamType.un1_P: 1066 - 1, ParamType.un1_Q: 1063 - 1} #1-2 drive
        elif housenumber == 2:
            register = {ParamType.un2_P: 1084 - 1, ParamType.un2_Q: 1081 - 1} #3-4 drive
        elif housenumber == 3:
            register = {ParamType.un3_P: 1102 - 1, ParamType.un3_Q: 1099 - 1} #5-6 drive

        return register

    def __init__(self):
        super(DisctrictInitializer, self).__init__()

class GridLabCyberPhysicalSystem(AbstractCyberPhysicalSystem):
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
        self._con = None

    def initialize(self, districtname, housename,
                   readparamlist=None, sicamregister=None, slave=None,
                   writeparamlist=None, acs800register=None):
        """

        initialize(self, readparamlist, sicamregister, writeparamlist, acs800register, slave)

        Initialize the ReadParam and the WriteParam

        :param housename: id of the slave house
        :param districtname: the district letter
        :param readparamlist: readparam list supported
        :param sicamregister: sicam modbus technical information
        :param writeparamlist: writeparam list supported, (required)
        :param acs800register: acs800 modbus technical information
        """
        self._districtunit = districtname

        if districtname not in definedhost.keys():
            raise Exception('Error no district name found')

        self._con = DisctrictInitializer.initializeHost(districtname)

        self._slave = slave
        self.rlist = readparamlist
        self._sicamregister = sicamregister

        if slave == None or readparamlist == None or sicamregister == None:
           self._slave, self._sicamregister, self.rlist = DisctrictInitializer.initializeReadRegisterParam(districtname, housename)

        if 'quantity' in self._sicamregister and self._sicamregister['quantity'] == len(self.rlist):
           pass
        else:
           raise Exception('ReadParam does not match the registers value')

        for r in self.rlist:
            self.readparamlist.append(ReadParam(r))

        self.wlist = writeparamlist
        self._acs800register = acs800register

        if writeparamlist != None:
            if acs800register == None:
                self._acs800register = DisctrictInitializer.initializeWriteRegisterParam(housename)
            if len(self._acs800register) != len(self.wlist):
                raise Exception('WwriteParam does not match the registers value')

            for w in self.wlist:
                if len(w) == 2:
                    self.writeparamlist.append(WriteParam(w[0], w[1]))
                if len(w) == 3:
                    self.writeparamlist.append(WriteParam(w[0], w[1], w[2]))
                else:
                    raise Exception('Error WriteParam cannot be created')

    def readParams(self):
        """

        readParams(self)

        Read params from the system using modbus over TCP.
        In this case all the data can be read in one time

        :return: read value
        """

        quantity = self._sicamregister['quantity']
        self._con['sicam'].send(self._slave,self._sicamregister['all'],quantity*2)# UL1-N,UL2-N,UL3-N,UNE,IL1,IL2,IL3,ILNE
        data = self._con['sicam'].receive(1024).encode('hex')

        #TODO check crc

        if len(data) < (6+8*quantity):
            return None
        if data[:6] == '000000':
            return None

        res = []
        for i in range(quantity):
            d = data[6+i*8:6 +(i+1)*8] #get data frame
            res.append(self._con['sicam'].measured_value_float_decode(d))

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
            if (paramtype not in self._oldwrite.keys()) or (paramtype in self._oldwrite.keys() and self._oldwrite[paramtype] != data):
                #print('update writing data')
                if self._con['acs800'].write_multiple_registers(self._acs800register[paramtype],[data]) == None:
                    #print('acs800 socket closed')
                    self._con['acs800'].open()
                    if self._con['acs800'].write_multiple_registers(self._acs800register[paramtype], [data]) == None:
                        #print('acs800 cannot opend socket')
                        pass
                self._oldwrite[paramtype] = data
