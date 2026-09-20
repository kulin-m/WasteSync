from pydantic import BaseModel
from typing import Optional
from app.models.bin import BinStatus

class BinBase(BaseModel):
    latitude: float
    longitude: float
    capacity: float
    height: float
    address: Optional[str] = None

class BinCreate(BinBase):
    pass

class BinUpdateTelemetry(BaseModel):
    current_garbage_height: float

class BinOut(BinBase):
    id: int
    current_garbage_height: float
    fill_percentage: float
    status: BinStatus

    class Config:
        from_attributes = True
