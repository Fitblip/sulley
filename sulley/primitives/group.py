from base import base

class group (base):
    def __init__ (self, name, values):
        """
        This primitive represents a list of static values, stepping through each one on mutation. You can tie a block
        to a group primitive to specify that the block should cycle through all possible mutations for *each* value
        within the group. The group primitive is useful for example for representing a list of valid opcodes.

        @type  name:   String
        @param name:   Name of group
        @type  values: List or raw data
        @param values: List of possible raw values this group can take.
        """

        super(group, self).__init__()

        self.name           = name
        self.values         = values
        self.fuzzable       = True

        self.s_type         = "group"
        self.value          = self.values[0]
        self.original_value = self.values[0]
        self.rendered       = ""
        self.fuzz_complete  = False
        self.mutant_index   = 0

        # sanity check that values list only contains strings (or raw data)
        if self.values:
            for val in self.values:
                assert type(val) is str, "Value list may only contain strings or raw data"


    def mutate (self):
        """
        Move to the next item in the values list.

        :rtype:  False
        :returns: False
        """

        if self.mutant_index == self.num_mutations():
            self.fuzz_complete = True

        # if fuzzing was disabled or complete, and mutate() is called, ensure the original value is restored.
        if not self.fuzzable or self.fuzz_complete:
            self.value = self.values[0]
            return False

        # step through the value list.
        self.value = self.values[self.mutant_index]

        # increment the mutation count.
        self.mutant_index += 1

        return True


    def num_mutations (self):
        """
        Number of values in this primitive.

        :rtype:  Integer
        :returns: Number of values in this primitive.
        """

        return len(self.values)
