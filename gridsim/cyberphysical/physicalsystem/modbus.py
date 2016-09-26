import socket
from .crc16modbus import _calculateCrcString

class ModBusOverTcp(object):
    def __init__(self, address, port):
        super(ModBusOverTcp, self).__init__()

        self.address = address
        self.port = port

        self.s = None

    def open(self):
        self.s = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.address, self.port))

    def send_raw(self,raw_message):
        totalsent = 0
        # while totalsent < MSGLEN:
        sent = self.s.send(raw_message)
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent

    def send(self, slave_address, register, quantity):
        q = str(quantity)
        hex_slave_address = hex(slave_address)
        hex_register = hex(register)
        string_msg = str(hex_slave_address).replace('0x','') + '03' + str(hex_register).replace('0x','') + q.rjust(4,'0')
        raw_msg = string_msg.decode('hex')

        crc = _calculateCrcString(raw_msg)

        raw_msg = raw_msg + crc

        #print raw_msg

        self.send_raw(raw_msg)

    def receive(self):
        chunks = []
        bytes_recd = 0
        #while bytes_recd < MSGLEN:
        chunk = self.s.recv(64)
        if chunk == '':
            raise RuntimeError("socket connection broken")
        chunks.append(chunk)
        bytes_recd = bytes_recd + len(chunk)
        return ''.join(chunks)

    def measured_value_float_decode(self,val):

        bframe = bin(int(val, 16))
        bframe = bframe[2:]
        bframe = bframe.rjust(32, '0')

        mantissa = bframe[len(bframe) - 23:]  # precision
        exp = int('0b' + bframe[len(bframe) - 23 - 8:9], 2)  # offset
        s = int('0b' + bframe[:1], 2)  # bit sign

        vmantissa = 0.

        for n,i in enumerate(str(mantissa),1):
            vmantissa = vmantissa + float(i)/(pow(2,n))

        res = pow(-1, s) + 0.
        res = res * pow(2, exp - 127)
        res = res * (1.0 + vmantissa)

        return res
