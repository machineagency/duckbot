from .Tool import Tool, ToolStateError

class Camera(Tool):
    def __init__(self, machine, index, name):
        super().__init__(machine, index, name)