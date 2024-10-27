from typing import List, Dict
from dataclasses import dataclass, field

from models.ImageInfo import ImageInfo
from utils.image_helper import resize_image_data


@dataclass
class VehicleData:
    vehicleId: str
    totalKm: int
    lastLiters: float
    lastCost: float
    addInfo: Dict[str, str] = field(default_factory=dict)
    images: List[ImageInfo] = field(default_factory=list)

    def add_image(self, image_data: ImageInfo, resize_image: bool = False, max_width: int = 800):
        if resize_image:
            image_data.imageData = resize_image_data(image_data.imageData, max_width)
        self.images.append(image_data)

    def to_dict(self):
        return {
            "vehicleId": self.vehicleId,
            "totalKm": self.totalKm,
            "lastLiters": self.lastLiters,
            "lastCost": self.lastCost,
            "addInfo": self.addInfo,
            "images": [image.__dict__ for image in self.images]
        }
