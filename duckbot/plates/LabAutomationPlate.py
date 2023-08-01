from .Plate import Plate, PlateStateError

class LabAutomationPlate(Plate):
    def __init__(self, name, num_slots, sharps_container):
        super().__init__(name, num_slots)
        self._sharps_container = sharps_container # true/false
        
    
    