from pydantic import BaseModel
from typing import Optional

class VehicleBase(BaseModel):
    vehicle_number: str
    capacity: float
    driver_id: Optional[int] = None
    status: str = "Available"

class VehicleCreate(VehicleBase):
    pass

class VehicleOut(VehicleBase):
    id: int

    class Config:
        from_attributes = True

class DepotBase(BaseModel):
    name: str = "Main Depot"
    latitude: float
    longitude: float
    address: Optional[str] = None

class DepotCreate(DepotBase):
    pass

class DepotOut(DepotBase):
    id: int

    class Config:
        from_attributes = True
