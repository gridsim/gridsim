"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.cyberphysical.external import Actor

from gridsim.iodata.input import CSVReader
from gridsim.timeseries import TimeSeriesObject

from gridsim.core import AbstractSimulationElement

from pqcontroller import ParamType

import struct

class PQFileReader(Actor,AbstractSimulationElement):

    def __init__(self, friendly_name, infile, outfile, readparamlist, writeparamlist):
        """

        __init__(self, friendly_name, infile, outfile, readparamlist, writeparamlist)

        Initialize the PQFileReader Actor with the readparam and writeparam dependency list.
        Datas are read from infile, and get to the simulation on getValue

        :param friendly_name: Element name id
        :param infile: csv file to read value from (P,Q)
        :param outfile: log the data out
        :param readparamlist: Read param to register on
        :param writeparamlist: Write param to register on
        """
        Actor.__init__(self)
        AbstractSimulationElement.__init__(self, friendly_name)

        self.readparamtype = readparamlist
        self.writeparamtype = writeparamlist

        self._infile = TimeSeriesObject(CSVReader(infile))
        self._outfile = open(outfile,'w')

        self._fileinput = {}
        #temp out storage for logging to file
        self._outstorage = {}
        #temp in storage for logging
        self._instorage = {}

        self._outlog = len(readparamlist)
        self._inlog = len(writeparamlist)

        self.readid = 0
        self.writeid = 0

    def initFile(self):
        """

        initFile(self)

        Initialize the File to read data from

        """
        self._fileinput[ParamType.un1_P] = 'pa'
        self._fileinput[ParamType.un1_Q] = 'qa'
        self._fileinput[ParamType.un2_P] = 'pb'
        self._fileinput[ParamType.un2_Q] = 'qb'
        self._fileinput[ParamType.un3_P] = 'pc'
        self._fileinput[ParamType.un3_Q] = 'qc'

        self._infile.load()

    def init(self):
       pass

    def reset(self):
        self.readid = 0

    def update(self, time, delta_time):
        self._infile.set_time(time)

    def calculate(self, time, delta_time):
        pass

    def notifyReadParam(self,paramtype,data):
        """

        notifyReadParam(self,paramtype,data)

        Log the measured data to the file
        """
        self.readid = self.readid + 1
        self._outstorage[paramtype] = data
        if self.readid == self._outlog:
            print 'notify', self._outstorage
            joined = ''
            for value in self._outstorage.values():
                joined = str(value) + ','

            if len(joined) > 1:
                joined = joined[:-1] + '\n'

            print 'notify linked list',joined
            self._outfile.write(str(joined))
            self._outfile.flush()
            self.readid = 0

    def getValue(self,paramtype):
        """

        getValue(self,paramtype)

        Read data from the file and update to the simulation the new value
        """
        if paramtype in self._fileinput.keys():
            val = getattr(self._infile,str(self._fileinput[paramtype]))
            self.writeid = self.writeid + 1
            self._instorage[paramtype] = val
            if self.writeid == self._inlog:
                print 'get value', self._instorage
                self.writeid = 0

            if 'p' in self._fileinput[paramtype]:
                val = val/22*10
            if 'q' in self._fileinput[paramtype]:
                val = (val - 1990) * -1 / 2.254

            return int(struct.pack('>h', val).encode('hex'), 16)

    def kill(self,time):
        """

        kill(self,time)

        close the file before after the end of the simulation
        """
        self._outfile.close()