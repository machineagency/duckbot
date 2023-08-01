from .Tool import Tool, ToolStateError
import os
import json

class Pipette(Tool):
    def __init__(self, machine, index, name, details):
        super().__init__(machine, index, name, details)
        self.has_tip = False
        self.min_range = 0
        self.max_range = None
        self.eject_start = None
        self.mm_to_ul = None
        
        self.load_config(details)
        
    def load_config(self, details):
        # check for the relevant config file for this pipette
        if not details:
            raise ToolStateError("Error: Specify the pipette model in your tool_types.json file")
        else:
            config_path = os.path.join(self.get_root_dir(), f'config/tools/{self._details}.json')
            if not os.path.isfile(config_path):
                raise ToolStateError(f"Error: Config file {self._details}.json does not exist!")
                
            with open(config_path, 'r') as f:
                config = json.load(f)
            try:
                self.max_range = config['max_range']
                self.eject_start = config['eject_start']
                self.mm_to_ul = config['mm_to_ul'] 
            except:
                raise ToolStateError("Error: Problem with provided configuration file.")
        
        # check that all information was provided
        if None in [self.max_range, self.eject_start, self.mm_to_ul]:
            raise ToolStateError("Error: Problem with provided configuration file.")
                
    def check_bounds(self, pos):
        if pos > self.max_range or pos < self.min_range:
            raise ToolStateError(f"Error: {pos} is out of bounds for the syringe!")
    
    def pickup_tip(self):
        if not self.has_tip:
            # do the pickup
            print('i picked up a tip!')
            self.has_tip = True
        else:
            raise ToolStateError("Error: Pipette already equipped with a tip.")

    
    def eject_tip(self):
        if self.has_tip:
            self._machine.move_to(v=0.95*self.max_range)
            self.aspirate_prime()
            print('i ejected a tip!')
            self.has_tip = False
        else:
            raise ToolStateError("Error: Pipette does not have tip to eject.")
    
    def aspirate(self, vol): # volume is in microliters. 50 is the max volume
        dv = vol* -1 * self.mm_to_ul
        end_pos = float(self._machine.get_position()['V']) + dv
        self.check_bounds(end_pos)
        self._machine.move_to(v=end_pos)
        
    def dispense(self, vol): # volume is in microliters. 50 is the max volume
        dv = vol * self.mm_to_ul
        end_pos = float(self._machine.get_position()['V']) + dv
        self.check_bounds(end_pos)
        self._machine.move_to(v=end_pos)      

    def aspirate_prime(self):
        self._machine.move_to(v=self.eject_start)