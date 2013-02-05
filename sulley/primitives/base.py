class base(object):
    """
    The primitive base class implements common functionality shared across most primitives.

    Most of these methods get overridden in their respective classes anyway.
    """

    def __init__(self):
        self.fuzz_complete  = False # this flag is raised when the mutations are exhausted.
        self.fuzz_library   = []    # library of static fuzz heuristics to cycle through.
        self.fuzzable       = True  # flag controlling whether or not the given primitive is to be fuzzed.
        self.mutant_index   = 0     # current mutation index into the fuzz library.
        self.original_value = None  # original value of primitive.
        self.rendered       = ""    # rendered value of primitive.
        self.value          = None  # current value of primitive.

    def mutate(self):
        """
        Mutate the primitive by stepping through the fuzz library, return False on completion.

        :rtype:  Boolean
        :returns: True on success, False otherwise.
        """

        # if we've ran out of mutations, raise the completion flag.
        if self.mutant_index == self.num_mutations():
            self.fuzz_complete = True

        # if fuzzing was disabled or complete, and mutate() is called, ensure the original value is restored.
        if not self.fuzzable or self.fuzz_complete:
            self.value = self.original_value
            return False

        # update the current value from the fuzz library.
        self.value = self.fuzz_library[self.mutant_index]

        # increment the mutation count.
        self.mutant_index += 1

        return True

    def num_mutations(self):
        """
        Calculate and return the total number of mutations for this individual primitive.

        :rtype:  Integer
        :returns: Number of mutated forms this primitive can take
        """
        return len(self.fuzz_library)


    def render(self):
        """
        Nothing fancy on render, simply return the value.
        """
        self.rendered = self.value
        return self.rendered

    def reset(self):
        """
        Reset this primitive to the starting mutation state.
        """
        self.fuzz_complete = False
        self.mutant_index = 0
        self.value = self.original_value
