from base import base

class static (base):
    def __init__ (self, value, name=None):
        """
        Primitive that contains static content.

        @type  value: Raw
        @param value: Raw static data
        @type  name:  String
        @param name:  (Optional, def=None) Specifying a name gives you direct access to a primitive
        """
        super(static, self).__init__()
        self.value         = self.original_value = value
        self.name          = name
        self.fuzzable      = False       # every primitive needs this attribute.
        self.mutant_index  = 0
        self.s_type        = "static"    # for ease of object identification
        self.rendered      = ""
        self.fuzz_complete = True


    def mutate (self):
        """
        Do nothing.

        :rtype:  False
        :returns: False
        """

        return False


    def num_mutations (self):
        """
        Return 0.

        :rtype:  0
        :returns: 0
        """

        return 0
