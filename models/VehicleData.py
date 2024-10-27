from typing import List, Dict
from dataclasses import dataclass, field

from models.ImageInfo import ImageInfo


@dataclass
class VehicleData:
    vehicleId: str
    totalKm: int
    lastLiters: float
    lastCost: float
    addInfo: Dict[str, str] = field(default_factory=dict)
    images: List[ImageInfo] = field(default_factory=list)

    def add_image(self, image_data: str, image_type: str, confidence: float, add_info: Dict[str, str],
                  description: str):
        image_info = ImageInfo(
            imageData=image_data,
            type=image_type,
            confidence=confidence,
            numOfSeq=1,
            addInfo=add_info,
            description=description
        )
        self.images.append(image_info)

    def to_dict(self):
        return {
            "vehicleId": self.vehicleId,
            "totalKm": self.totalKm,
            "lastLiters": self.lastLiters,
            "lastCost": self.lastCost,
            "addInfo": self.addInfo,
            "images": [image.__dict__ for image in self.images]
        }
