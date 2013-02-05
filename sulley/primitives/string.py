from base import base

class string (base):
    # store fuzz_library as a class variable to avoid copying the ~70MB structure across each instantiated primitive.
    fuzz_library = []

    def __init__ (self, value, size=-1, padding="\x00", encoding="ascii", fuzzable=True, max_len=0, name=None):
        """
        Primitive that cycles through a library of "bad" strings. The class variable 'fuzz_library' contains a list of
        smart fuzz values global across all instances. The 'this_library' variable contains fuzz values specific to
        the instantiated primitive. This allows us to avoid copying the near ~70MB fuzz_library data structure across
        each instantiated primitive.

        @type  value:    String
        @param value:    Default string value
        @type  size:     Integer
        @param size:     (Optional, def=-1) Static size of this field, leave -1 for dynamic.
        @type  padding:  Character
        @param padding:  (Optional, def="\\x00") Value to use as padding to fill static field size.
        @type  encoding: String
        @param encoding: (Optonal, def="ascii") String encoding, i.e. utf_16_le for Microsoft Unicode.
        @type  fuzzable: Boolean
        @param fuzzable: (Optional, def=True) Enable/disable fuzzing of this primitive
        @type  max_len:  Integer
        @param max_len:  (Optional, def=0) Maximum string length
        @type  name:     String
        @param name:     (Optional, def=None) Specifying a name gives you direct access to a primitive
        """
        super(string, self).__init__()
        self.value         = self.original_value = value
        self.size          = size
        self.padding       = padding
        self.encoding      = encoding
        self.fuzzable      = fuzzable
        self.name          = name

        self.s_type        = "string"  # for ease of object identification
        self.rendered      = ""        # rendered value
        self.fuzz_complete = False     # flag if this primitive has been completely fuzzed
        self.mutant_index  = 0         # current mutation number

        # add this specific primitives repitition values to the unique fuzz library.
        self.this_library =\
        [
            self.value * 2,
            self.value * 10,
            self.value * 100,

            # UTF-8
            self.value * 2   + "\xfe",
            self.value * 10  + "\xfe",
            self.value * 100 + "\xfe",
            ]

        # if the fuzz library has not yet been initialized, do so with all the global values.
        if not self.fuzz_library:
            string.fuzz_library  =\
            [
                # omission.
                "",

                # strings ripped from spike (and some others I added)
                "/.:/"  + "A"*5000 + "\x00\x00",
                "/.../" + "A"*5000 + "\x00\x00",
                "/.../.../.../.../.../.../.../.../.../.../",
                "/../../../../../../../../../../../../etc/passwd",
                "/../../../../../../../../../../../../boot.ini",
                "..:..:..:..:..:..:..:..:..:..:..:..:..:",
                "\\\\*",
                "\\\\?\\",
                "/\\" * 5000,
                "/." * 5000,
                "!@#$%%^#$%#$@#$%$$@#$%^^**(()",
                "%01%02%03%04%0a%0d%0aADSF",
                "%01%02%03@%04%0a%0d%0aADSF",
                "/%00/",
                "%00/",
                "%00",
                "%u0000",
                "%\xfe\xf0%\x00\xff",
                "%\xfe\xf0%\x01\xff" * 20,

                # format strings.
                "%n"     * 100,
                "%n"     * 500,
                "\"%n\"" * 500,
                "%s"     * 100,
                "%s"     * 500,
                "\"%s\"" * 500,

                # command injection.
                "|touch /tmp/SULLEY",
                ";touch /tmp/SULLEY;",
                "|notepad",
                ";notepad;",
                "\nnotepad\n",

                # SQL injection.
                "1;SELECT%20*",
                "'sqlattempt1",
                "(sqlattempt2)",
                "OR%201=1",

                # some binary strings.
                "\xde\xad\xbe\xef",
                "\xde\xad\xbe\xef" * 10,
                "\xde\xad\xbe\xef" * 100,
                "\xde\xad\xbe\xef" * 1000,
                "\xde\xad\xbe\xef" * 10000,
                "\x00"             * 1000,

                # miscellaneous.
                "\r\n" * 100,
                "<>" * 500,         # sendmail crackaddr (http://lsd-pl.net/other/sendmail.txt)
            ]

            # add some long strings.
            self.add_long_strings("A")
            self.add_long_strings("B")
            self.add_long_strings("1")
            self.add_long_strings("2")
            self.add_long_strings("3")
            self.add_long_strings("<")
            self.add_long_strings(">")
            self.add_long_strings("'")
            self.add_long_strings("\"")
            self.add_long_strings("/")
            self.add_long_strings("\\")
            self.add_long_strings("?")
            self.add_long_strings("=")
            self.add_long_strings("a=")
            self.add_long_strings("&")
            self.add_long_strings(".")
            self.add_long_strings(",")
            self.add_long_strings("(")
            self.add_long_strings(")")
            self.add_long_strings("]")
            self.add_long_strings("[")
            self.add_long_strings("%")
            self.add_long_strings("*")
            self.add_long_strings("-")
            self.add_long_strings("+")
            self.add_long_strings("{")
            self.add_long_strings("}")
            self.add_long_strings("\x14")
            self.add_long_strings("\xFE")   # expands to 4 characters under utf16
            self.add_long_strings("\xFF")   # expands to 4 characters under utf16

            # add some long strings with null bytes thrown in the middle of it.
            for length in [128, 256, 1024, 2048, 4096, 32767, 0xFFFF]:
                s = "B" * length
                s = s[:len(s)/2] + "\x00" + s[len(s)/2:]
                string.fuzz_library.append(s)

            # if the optional file '.fuzz_strings' is found, parse each line as a new entry for the fuzz library.
            try:
                fh = open(".fuzz_strings", "r")

                for fuzz_string in fh.readlines():
                    fuzz_string = fuzz_string.rstrip("\r\n")

                    if fuzz_string != "":
                        string.fuzz_library.append(fuzz_string)

                fh.close()
            except:
                pass

        # delete strings which length is greater than max_len.
        if max_len > 0:
            if any(len(s) > max_len for s in self.this_library):
                self.this_library = list(set([s[:max_len] for s in self.this_library]))

            if any(len(s) > max_len for s in self.fuzz_library):
                self.fuzz_library = list(set([s[:max_len] for s in self.fuzz_library]))


    def add_long_strings (self, sequence):
        """
        Given a sequence, generate a number of selectively chosen strings lengths of the given sequence and add to the
        string heuristic library.

        @type  sequence: String
        @param sequence: Sequence to repeat for creation of fuzz strings.
        """

        for length in [128, 255, 256, 257, 511, 512, 513, 1023, 1024, 2048, 2049, 4095, 4096, 4097, 5000, 10000, 20000,
                       32762, 32763, 32764, 32765, 32766, 32767, 32768, 32769, 0xFFFF-2, 0xFFFF-1, 0xFFFF, 0xFFFF+1,
                       0xFFFF+2, 99999, 100000, 500000, 1000000]:

            long_string = sequence * length
            string.fuzz_library.append(long_string)


    def mutate (self):
        """
        Mutate the primitive by stepping through the fuzz library extended with the "this" library, return False on
        completion.

        :rtype:  Boolean
        :returns: True on success, False otherwise.
        """

        # loop through the fuzz library until a suitable match is found.
        while 1:
            # if we've ran out of mutations, raise the completion flag.
            if self.mutant_index == self.num_mutations():
                self.fuzz_complete = True

            # if fuzzing was disabled or complete, and mutate() is called, ensure the original value is restored.
            if not self.fuzzable or self.fuzz_complete:
                self.value = self.original_value
                return False

            # update the current value from the fuzz library.
            self.value = (self.fuzz_library + self.this_library)[self.mutant_index]

            # increment the mutation count.
            self.mutant_index += 1

            # if the size parameter is disabled, break out of the loop right now.
            if self.size == -1:
                break

            # ignore library items greather then user-supplied length.
            # XXX - might want to make this smarter.
            if len(self.value) > self.size:
                continue

            # pad undersized library items.
            if len(self.value) < self.size:
                self.value += self.padding * (self.size - len(self.value))
                break

        return True


    def num_mutations (self):
        """
        Calculate and return the total number of mutations for this individual primitive.

        :rtype:  Integer
        :returns: Number of mutated forms this primitive can take
        """

        return len(self.fuzz_library) + len(self.this_library)


    def render (self):
        """
        Render the primitive, encode the string according to the specified encoding.
        """

        # try to encode the string properly and fall back to the default value on failure.
        try:
            self.rendered = str(self.value).encode(self.encoding)
        except:
            self.rendered = self.value

        return self.rendered
