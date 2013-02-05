import struct
from base import base

class bit_field (base):
    def __init__ (self, value, width, max_num=None, endian="<", format="binary", signed=False, full_range=False, fuzzable=True, name=None):
        """
        The bit field primitive represents a number of variable length and is used to define all other integer types.

        Used to sub-class out words, qwords, bytes, and any other binary blocks.

        :type  value:      Integer
        :param value:      Default integer value
        :type  width:      Integer
        :param width:      Width of bit fields
        :type  endian:     Character
        :param endian:     (Optional, def=LITTLE_ENDIAN) Endianess of the bit field (LITTLE_ENDIAN: <, BIG_ENDIAN: >)
        :type  format:     String
        :param format:     (Optional, def=binary) Output format, "binary" or "ascii"
        :type  signed:     Boolean
        :param signed:     (Optional, def=False) Make size signed vs. unsigned (applicable only with format="ascii")
        :type  full_range: Boolean
        :param full_range: (Optional, def=False) If enabled the field mutates through *all* possible values.
        :type  fuzzable:   Boolean
        :param fuzzable:   (Optional, def=True) Enable/disable fuzzing of this primitive
        :type  name:       String
        :param name:       (Optional, def=None) Specifying a name gives you direct access to a primitive
        """

        assert(type(value) is int or type(value) is long)
        assert(type(width) is int or type(value) is long)

        super(bit_field,self).__init__()
        self.value         = self.original_value = value
        self.width         = width
        self.max_num       = max_num
        self.endian        = endian
        self.format        = format
        self.signed        = signed
        self.full_range    = full_range
        self.fuzzable      = fuzzable
        self.name          = name

        self.rendered      = ""        # rendered value
        self.fuzz_complete = False     # flag if this primitive has been completely fuzzed
        self.fuzz_library  = []        # library of fuzz heuristics
        self.mutant_index  = 0         # current mutation number

        if self.max_num is None:
            self.max_num = self.to_decimal("1" * width)

        assert(type(self.max_num) is int or type(self.max_num) is long)

        # build the fuzz library.
        if self.full_range:
            # add all possible values.
            for i in xrange(0, self.max_num):
                self.fuzz_library.append(i)
        else:
            # try only "smart" values.
            self.add_integer_boundaries(0)
            self.add_integer_boundaries(self.max_num / 2)
            self.add_integer_boundaries(self.max_num / 3)
            self.add_integer_boundaries(self.max_num / 4)
            self.add_integer_boundaries(self.max_num / 8)
            self.add_integer_boundaries(self.max_num / 16)
            self.add_integer_boundaries(self.max_num / 32)
            self.add_integer_boundaries(self.max_num)

        # if the optional file '.fuzz_ints' is found, parse each line as a new entry for the fuzz library.
        try:
            fh = open(".fuzz_ints", "r")

            for fuzz_int in fh.readlines():
                # convert the line into an integer, continue on failure.
                try:
                    fuzz_int = long(fuzz_int, 16)
                except:
                    continue

                if fuzz_int <= self.max_num:
                    self.fuzz_library.append(fuzz_int)

            fh.close()
        except:
            pass


    def add_integer_boundaries (self, integer):
        """
        Add the supplied integer and border cases to the integer fuzz heuristics library.

        :type  integer: Int
        :param integer: Integer to append to fuzz heuristics
        """

        for i in xrange(-10, 10):
            case = integer + i

            # ensure the border case falls within the valid range for this field.
            if 0 <= case <= self.max_num:
                if case not in self.fuzz_library:
                    self.fuzz_library.append(case)


    def render (self):
        """
        Render the primitive.
        """

        #
        # binary formatting.
        #

        if self.format == "binary":
            bit_stream = ""
            rendered   = ""

            # pad the bit stream to the next byte boundary.
            if self.width % 8 == 0:
                bit_stream += self.to_binary()
            else:
                bit_stream  = "0" * (8 - (self.width % 8))
                bit_stream += self.to_binary()

            # convert the bit stream from a string of bits into raw bytes.
            for i in xrange(len(bit_stream) / 8):
                chunk = bit_stream[8*i:8*i+8]
                rendered += struct.pack("B", self.to_decimal(chunk))

            # if necessary, convert the endianess of the raw bytes.
            if self.endian == "<":
                rendered = list(rendered)
                rendered.reverse()
                rendered = "".join(rendered)

            self.rendered = rendered

        #
        # ascii formatting.
        #

        else:
            # if the sign flag is raised and we are dealing with a signed integer (first bit is 1).
            if self.signed and self.to_binary()[0] == "1":
                max_num = self.to_decimal("0" + "1" * (self.width - 1))
                # chop off the sign bit.
                val = self.value & max_num

                # account for the fact that the negative scale works backwards.
                val = max_num - val

                # toss in the negative sign.
                self.rendered = "%d" % ~val

            # unsigned integer or positive signed integer.
            else:
                self.rendered = "%d" % self.value

        return self.rendered


    def to_binary (self, number=None, bit_count=None):
        """
        Convert a number to a binary string.

        :type  number:    Integer
        :param number:    (Optional, def=self.value) Number to convert
        :type  bit_count: Integer
        :param bit_count: (Optional, def=self.width) Width of bit string

        :rtype:  String
        :returns: Bit string
        """

        if number is None:
            number = self.value

        if bit_count is None:
            bit_count = self.width

        return "".join(map(lambda x:str((number >> x) & 1), range(bit_count -1, -1, -1)))


    def to_decimal (self, binary):
        """
        Convert a binary string to a decimal number.

        :type  binary: String
        :param binary: Binary string

        :rtype:  Integer
        :returns: Converted bit string
        """

        return int(binary, 2)
