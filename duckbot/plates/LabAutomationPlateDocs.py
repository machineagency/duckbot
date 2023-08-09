from .Plate import Plate, PlateStateError, PlateConfigurationError

import os
import json
import math

# The Automation Bed Plate and well plates are oriented as follows:                                          

#                          BED PLATE TOP VIEW                          WELL PLATE TOP VIEW                                                                                            
#         Machine Origin                                     Machine Origin               Slot Calibration                                                                     
#             (0,0)                                              (0,0)                        Position                                                        
#                +------------------------------------+               +--------------------+                                                                      
#                |   +------+   +------+   +------+   |               | Well          Well |                                                                            
#                |   |      |   |      |   |      |   |               |  i1            A1  |                                                                                                
#                |   |      |   |      |   |      |   |               |                    |                                                                        
#                |   |  0   |   |  1   |   |  2   |   |               |                    |                                                                        
#                |   |      |   |      |   |      |   |               |                    |                                                                        
#                |   |      |   |      |   |      |   |               |                    |                                                                        
#                |   +------+   +------+   +------+   | Tool Rack     |                    |                                                                        
#                |   +------+   +------+   +------+   |               |                    |                                                                                            
#                |   |      |   |      |   |      |   |               |                    |                                                                        
#                |   |      |   |      |   |      |   |               |                    |                                                                        
#                |   |  5   |   |  4   |   |  3   |   |               |                    |                                                                                            
#   Power Supply |   |      |   |      |   |      |   |               |                    |                                                                                             
#                |   |      |   |      |   |      |   |               | Well          Well |                                                                                            
#                |   +------+   +------+   +------+   |               |  ij            Aj  |                                                                                            
#                +------------------------------------+               +--------------------+           
#                                                        

class LabAutomationPlate(Plate):
    """Setup a lab automation plate with relevant labware."""
    def __init__(self, machine, name, config):
        """Set default values and load in plate configuration."""
        super().__init__(machine, name)

        # Load the config file
        config_path = os.path.join(self.get_root_dir(), f"config/machine/{config}.json")
        if not os.path.isfile(config_path):
            raise PlateConfigurationError(f"Error: config file at {config_path} does not exist")
        with open(config_path, 'r') as f:
            config_contents = json.load(f)
            
        self.num_slots = len(config_contents)
        self.slots = {}
        for slot_index, origin in config_contents.items():
            slot_index = int(slot_index)
            self.slots[slot_index] = {}
            self.slots[slot_index]['origin'] = [float(i) for i in origin]
            self.slots[slot_index]['labware'] = None
            
    def load_labware(self, slot_index: int, labware_name: str):
        """Load labware into a slot index."""
        # Load the labware configuration
        labware_config_path = os.path.join(self.get_root_dir(), f"config/labware/{labware_name}.json")
        if not os.path.isfile(labware_config_path):
            raise PlateConfigurationError(f"Error: Labware config file {labware_config_path} does not exist")
        with open(labware_config_path, 'r') as f:
            config_contents = json.load(f)
        slot = self.slots[slot_index]
        slot['labware'] = labware_name
        for key, value in config_contents.items():
            slot[key] = value
        
        # Calculate and store information for finding wells.
        column_count = slot['column_count']
        row_count = slot['row_count']
        max_row_letter = chr(ord('@')+row_count) # Labware rows are identified with letters
        
        # Find the machine coordinates by adding labware calibration points to the slot reference position. 
        # The slot reference position is calibrated to be the corner closest to well A1. 
        a = [sum(x) for x in zip(slot['calibration_positions']["A1"], slot['origin'])]
        slot['calibration_positions']["A1"] = a
        b = [sum(x) for x in zip(slot['calibration_positions'][f"A{column_count}"], slot['origin'])]
        slot['calibration_positions'][f"A{column_count}"] = b
        c = [sum(x) for x in zip(slot['calibration_positions'][f"{max_row_letter}{column_count}"], slot['origin'])]
        slot['calibration_positions'][f"{max_row_letter}{column_count}"] = c

        # Compute width, height, and well spacing from the configuration file.
        labware_width = math.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)
        labware_height = math.sqrt((c[0] - b[0])**2 + (c[1] - b[1])**2)
        slot['labware_width'] = labware_width
        slot['labware_height'] = labware_height
        slot['x_spacing'] = slot['labware_width'] / (column_count - 1)
        slot['y_spacing'] = slot['labware_height'] / (row_count - 1)
        
        # Machine and camera axes might be slightly skewed; average the redundant angle measurement.
        theta1 = math.asin((b[1] - a[1]) / labware_width)
        theta2 = math.asin((c[0] - b[0]) / labware_height)
        theta = (theta1 + theta2)/2
        slot['theta'] = theta
            
    def get_well_position(self, slot_index, well_id):
        """Return machine coordinates for a well id in a bed plate slot."""
        if self.slots[slot_index]['labware'] is None:
            raise PlateStateError(f"Error: No labware loaded into slot {slot_index}")
            
        row_letter = well_id[0]
        row = int(ord(row_letter.lower()) - 96)
        column = int(well_id[1:])
        slot = self.slots[slot_index]
        
        if row <= 0 or column <= 0 or row > slot['row_count'] or column > slot["column_count"]:
            raise PlateStateError("Error: Well ID is out of range for this labware.")
        
        # Translate and rotate from A1 to the desired well.
        row_index = row - 1
        column_index = column - 1
        a1 = slot['calibration_positions']["A1"]
        theta = slot['theta']
        x = column_index * slot['x_spacing']
        y = row_index * slot['y_spacing']
        
        # ToDo: Check this on the machine
        # 2D rotation:
        x_rotated = a1[0] + x * math.cos(theta) - y * math.sin(theta)
        y_rotated = a1[1] - (x * math.sin(theta) + y * math.cos(theta))
        
        x_nominal = a1[0] + x
        y_nominal = a1[1] - y
        
        
        # ToDo: return just the rotated values, assuming the work
        return [x_nominal, y_nominal, x_rotated, y_rotated]
            
        
            
        

    