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
