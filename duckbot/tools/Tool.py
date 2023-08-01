class ToolStateError(Exception):
    """Raise this error if the tool is in the wrong state to perform such a command."""
    pass

class Tool:
    def __init__(self, machine, index, name):
        self._machine = machine
        self._index = index
        self._name = name