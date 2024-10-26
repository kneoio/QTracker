from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class ImageInfo:
    imageData: str
    type: str
    confidence: float
    addInfo: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
