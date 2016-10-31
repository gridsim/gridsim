"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.core import AbstractSimulationElement
from gridsim.cyberphysical.external import Actor

from gridsim.iodata.input import CSVReader
from gridsim.timeseries import TimeSeriesObject

from paramtype import ParamType

class PQFileReader(Actor,AbstractSimulationElement):

    def __init__(self, friendly_name, infile, outfile, readparamlist, writeparamlist):
        """

        __init__(self, friendly_name, infile, outfile, readparamlist, writeparamlist)

        Initialize the PQFileReader Actor with the readparam and writeparam dependency list.
        Datas are read from infile, and get to the simulation on getValue function call

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

        self._fileinput = {ParamType.un1_P:'pa',ParamType.un1_Q:'qa',
                           ParamType.un2_P:'pb',ParamType.un2_Q:'qb',
                           ParamType.un3_P:'pc',ParamType.un3_Q:'qc'}

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
        print paramtype,data
        if self.readid == self._outlog:
            print 'notify', self._outstorage
            joined = ''
            for value in self._outstorage.values():
                joined = joined + str(value) + ','

            if len(joined) > 1:
                joined = joined[:-1] + '\n'

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

            return val

    def kill(self,time):
        """

        kill(self,time)

        close the file before after the end of the simulation
        """
        self._outfile.close()