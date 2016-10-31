"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.cyberphysical.core import Converter

import struct

class QConverter(Converter):
    def __init__(self, lmin, lmax, ldefault=0):
        """

        __init__(self)

        convert the data to a writable value for the simulation

        """
        super(QConverter, self).__init__(lmin,lmax,ldefault)

    def call(self,data):
        """

        call(self,data)

        convert reactive power

        :param data: data to convert
        :return: the converted value
        """

        if data < self.lmin or data > self.lmax:
            data = self.ldefault

        data = (data - 1990) / -2.254
        return int(struct.pack('>h', data).encode('hex'), 16)

class PConverter(Converter):
    def __init__(self, lmin, lmax, ldefault=0):
        """

        __init__(self)

        convert the data to a writable value for the simulation

        """
        super(PConverter, self).__init__(lmin,lmax,ldefault)

    def call(self,data):
        """

        call(self,data)

        convert active power

        :param data, data to convert
        :return the converted value
        """
        if data < self.lmin or data > self.lmax:
            data = self.ldefault

        data = data * 10 / 22 #*10
        return int(struct.pack('>h', data).encode('hex'), 16)


