import dataclasses
import enum

class RenderType(enum.Enum):
    INPUT_BOX = "INPUT_BOX"
    RESPONSE_BOX = "RESPONSE_BOX"
    GRAPH = "GRAPH"
    TABLE = "TABLE"

@dataclasses.dataclass
class Renderable:
    type: RenderType
    content: str
    
    def to_dict(self):
            return {
                "type": self.type.value,
                "content": self.content
            }