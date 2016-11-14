"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.core import AbstractSimulationElement
from gridsim.cyberphysical.external import Actor
from gridsim.cyberphysical.simulation import CyberPhysicalModuleListener

from gridsim.iodata.input import CSVReader
from gridsim.timeseries import TimeSeriesObject

import collections

class PQFileReader(Actor,AbstractSimulationElement,CyberPhysicalModuleListener):

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
        self._outfileinit = False

        self._fileinput = {}
        #temp out storage for logging to file
        self._outstorage = {}
        #temp in storage for logging
        self._instorage = {}

        self._outlog = len(readparamlist)
        self._inlog = len(writeparamlist)

        self.readid = 0
        self.writeid = 0

    def initFile(self, opcode):
        """

        initFile(self)

        Initialize the File to read data from
        and prepare the output file
        """
        self._fileinput = opcode
        self._tempstat = {}

        for k,t in opcode.items():
            attr = str(t[0]) + str(t[1]) + str(t[2])
            self._tempstat[attr] = k

        self._infile.load()

    def init(self):
       pass

    def reset(self):
        self.readid = 0

    def update(self, time, delta_time):
        self._infile.set_time(time)

    def calculate(self, time, delta_time):
        pass

    def cyberphysicalReadBegin(self):
        pass

    def cyberphysicalReadEnd(self):
        """

        cyberphysicalReadEnd(self)

        print at the end of the step all the notified value inside a csv file.
        """
        self._outstorage = collections.OrderedDict(sorted(self._outstorage.items()))
        if not self._outfileinit:
            self._outfileinit = True
            title = ','.join(i.replace('ParamType.','') for i in self._outstorage.keys())
            self._outfile.write(title + '\n')
        data = ','.join(str(i) for i in self._outstorage.values())
        self._outfile.write(data + '\n')

    def notifyReadParam(self,info,data):
        """

        notifyReadParam(self,paramtype,data)

        Log the measured data to the file
        """
        attr = ''
        if len(info) == 2:
            attr = str(info[1][0]) + str(info[1][1]) + str(info[0])
        self._outstorage[attr] = data #create

    def getValue(self,info):
        """

        getValue(self,paramtype)

        Read data from the file and update to the simulation the new value
        """
        if len(info) == 2:
            attr = str(info[0]) + str(info[1][0]) + str(info[1][1])
        else:
            return 0

        if attr in self._tempstat.keys():
            val = getattr(self._infile,str(self._tempstat[attr]))
            self.writeid = self.writeid + 1
            self._instorage[attr] = val
            if self.writeid == self._inlog:
                print 'get value', self._instorage
                self.writeid = 0

            return val

    def cyberphysicalModuleEnd(self):

        print 'end simulation from PQFileReader'
        self._outfile.close()