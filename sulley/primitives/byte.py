import struct
from bit_field import bit_field

class byte (bit_field):
    def __init__ (self, value, endian="<", format="binary", signed=False, full_range=False, fuzzable=True, name=None):
        self.s_type  = "byte"
        if type(value) not in [int, long]:
            value       = struct.unpack(endian + "B", value)[0]

        bit_field.__init__(self, value, 8, None, endian, format, signed, full_range, fuzzable, name)
