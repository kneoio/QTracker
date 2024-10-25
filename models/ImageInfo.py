from dataclasses import dataclass

@dataclass
class ImageInfo:
    imageData: str
    type: str
    confidence: float

