import dataclasses
import enum

class RenderType(enum.Enum):
    INPUT_BOX = "INPUT_BOX"
    RESPONSE_BOX = "RESPONSE_BOX"
    GRAPH = "GRAPH"
    NEW_GRAPH = "NEW_GRAPH"
    TABLE = "TABLE"

@dataclasses.dataclass
class Renderable:
    type: RenderType
    content: str
    code: str = ""
    function_name: str = ""
    
    def to_dict(self):
            return {
                "type": self.type.value,
                "content": self.content,
                "code": self.code,
                "function_name": self.function_name
            }