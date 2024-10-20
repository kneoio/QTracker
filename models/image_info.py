# image_info.py
from typing import Dict
from dataclasses import dataclass

@dataclass
class ImageInfo:
    imageData: str
    type: str
    confidence: float
    addInfo: Dict[str, str]
    description: str
