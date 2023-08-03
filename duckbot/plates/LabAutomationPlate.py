from .Plate import Plate, PlateStateError

import os
import json

class LabAutomationPlate(Plate):
    def __init__(self, machine, name,  config_name):
        super().__init__(machine, name)
        
        with open(os.path.join(self.get_root_dir(), f"config/machine/{config_name}.json"), 'r') as f:
            config = json.load(f)
        
        for key, value in config.items():
            print(key)
            print(value)
        
    
    