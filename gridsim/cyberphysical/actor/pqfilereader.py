"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.core import AbstractSimulationElement
from gridsim.cyberphysical.element import Actor
from gridsim.cyberphysical.simulation import CyberPhysicalModuleListener

from gridsim.iodata.input import CSVReader
from gridsim.timeseries import TimeSeriesObject

from gridsim.decorators import accepts, returns

import collections


class PQFileReader(Actor, AbstractSimulationElement, CyberPhysicalModuleListener):
    @accepts(((1, 2, 3), str), ((4, 5), list))
    def __init__(self, friendly_name, in_file_name, out_file_name, read_params, write_params):
        """
        __init__(self, friendly_name, infile, outfile, read_params, write_params)

        Initialize the PQFileReader Actor with the read_params and write_params dependency list.
        Data are read from infile, and get to the simulation on getValue function call.

        :param friendly_name: Element name id
        :param in_file_name: csv file to read value from (P,Q)
        :param out_file_name: log the data out
        :param read_params: Read param to register on
        :param write_params: Write param to register on
        """
        Actor.__init__(self)
        AbstractSimulationElement.__init__(self, friendly_name)

        self.read_params = read_params
        self.write_params = write_params

        self._in_opcode = {}
        self._in_file = TimeSeriesObject(CSVReader(in_file_name))

        # temp out storage for logging to file
        self._out_log = {}
        self._init_out_file = False
        self._out_file = open(out_file_name, 'w')

    @accepts((1, dict))
    def initFile(self, opcode):
        """
        initFile(self)

        Initialize the File to read data from,
        and prepare the output file.
        """
        for k, t in opcode.items():
            self._in_opcode[t] = k
        self._in_file.load()

    def reset(self):
        pass

    def update(self, time, delta_time):
        self._in_file.set_time(time)

    def calculate(self, time, delta_time):
        pass

    def cyberphysical_read_end(self):
        # push all the data after the read is finished in the log file

        self._out_log = collections.OrderedDict(sorted(self._out_log.items()))
        if not self._init_out_file:
            self._init_out_file = True
            title = ','.join(i.replace('ParamType.', '') for i in self._out_log.keys())
            self._out_file.write(title + '\n')
        data = ','.join(str(i) for i in self._out_log.values())
        self._out_file.write(data + '\n')
        self._out_file.flush()

    @accepts((2, (int, float)))
    def notify_read_param(self, read_param, data):
        # save data to temp list
        self._out_log[str(read_param)] = data

    @returns((int, float))
    def get_value(self, write_param):
        # get the new data from the file based on write_param
        if write_param in self._in_opcode.keys():
            val = getattr(self._in_file, str(self._in_opcode[write_param]))
            return val
        return 0

    def cyberphysical_module_end(self):
        print 'end simulation from PQFileReader'

        if not self._out_file is None:
            self._out_file.close()
