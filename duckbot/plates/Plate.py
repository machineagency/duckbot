class PlateStateError(Exception):
    """Raise this error if the plate is in the wrong state to perform such a command."""
    pass

class Plate:
    def __init__(self, name, num_slots):
        self._name = name
        self._num_slots = num_slots