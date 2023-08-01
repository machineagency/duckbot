from pathlib import Path

class ToolStateError(Exception):
    """Raise this error if the tool is in the wrong state to perform such a command."""
    pass

class Tool:
    def __init__(self, machine, index, name, details):
        self._machine = machine
        self._index = index
        self._name = name
        self._details = details
    
    def get_root_dir(self):
        return Path(__file__).parent.parent.parent