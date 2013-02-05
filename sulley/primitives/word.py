import struct
from bit_field import bit_field

class word (bit_field):
    def __init__ (self, value, endian="<", format="binary", signed=False, full_range=False, fuzzable=True, name=None):
        self.s_type  = "word"
        if type(value) not in [int, long]:
            value = struct.unpack(endian + "H", value)[0]

        bit_field.__init__(self, value, 16, None, endian, format, signed, full_range, fuzzable, name)
