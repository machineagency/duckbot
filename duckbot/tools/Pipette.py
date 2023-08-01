from .Tool import Tool, ToolStateError

class Pipette(Tool):
    def __init__(self, machine, index, name):
        super().__init__(machine, index, name)
        self.has_tip = False

    
    def pickup_tip(self):
        if not self.has_tip:
            # do the pickup
            print('i picked up a tip!')
            self.has_tip = True
        else:
            raise ToolStateError("Error: Pipette already equipped with a tip.")

    
    def eject_tip(self):
        if self.has_tip:
            # do the eject
            print('i ejected a tip!')
            self.has_tip = False
        else:
            raise ToolStateError("Error: Pipette does not have tip to eject.")
    
    def aspirate(self, vol):
        print("picked up some liquid!")

    def dispense(self, vol):
        print("dispensed some liquid")
    