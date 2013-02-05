import struct
from bit_field import bit_field

class qword (bit_field):
    def __init__ (self, value, endian="<", format="binary", signed=False, full_range=False, fuzzable=True, name=None):
        self.s_type  = "qword"
        if type(value) not in [int, long]:
            value = struct.unpack(endian + "Q", value)[0]

        bit_field.__init__(self, value, 64, None, endian, format, signed, full_range, fuzzable, name)
