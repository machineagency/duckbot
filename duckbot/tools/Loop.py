from .Tool import Tool, ToolStateError

class Loop(Tool):
    def __init__(self, machine, index, name):
        super().__init__(machine, index, name)

    