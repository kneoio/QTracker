import logging
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)


class Vehicle:
    def __init__(self, vehicle_data):
        self.id = vehicle_data.get("id")
        self.author = vehicle_data.get("author")
        self.reg_date = vehicle_data.get("regDate")
        self.last_modifier = vehicle_data.get("lastModifier")
        self.last_modified_date = vehicle_data.get("lastModifiedDate")
        self.vehicle_type = vehicle_data.get("vehicleType")
        self.brand = vehicle_data.get("brand")
        self.fuel_type = vehicle_data.get("fuelType")
        self.status = vehicle_data.get("status")
        self.localized_name = vehicle_data.get("localizedName", {})


class Owner:
    def __init__(self, telegram_name, vehicles):
        self.id = None
        self.author = None
        self.reg_date = None
        self.last_modifier = None
        self.last_modified_date = None
        self.telegram_name = telegram_name
        self.localized_name = {}
        self.vehicles: List[Vehicle] = vehicles

    @classmethod
    def from_response(cls, data):
        doc_data = data.get("payload", {}).get("docData", {})
        owner = cls(doc_data.get("telegramName"))
        owner.id = doc_data.get("id")
        owner.author = doc_data.get("author")
        owner.reg_date = doc_data.get("regDate")
        owner.last_modifier = doc_data.get("lastModifier")
        owner.last_modified_date = doc_data.get("lastModifiedDate")
        owner.localized_name = doc_data.get("localizedName", {})

        vehicles_data = doc_data.get("vehicles", [])
        owner.vehicles = [Vehicle(vehicle) for vehicle in vehicles_data]

        return owner

    def get_first_vehicle(self) -> Optional[Vehicle]:
        return self.vehicles[0] if self.vehicles else None
