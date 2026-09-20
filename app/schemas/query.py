from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.query import QueryType, QueryStatus

class QueryCreate(BaseModel):
    citizen_name: str
    address: str
    query_text: str
    query_type: QueryType = QueryType.CLEANLINESS_ISSUE
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class QueryStatusUpdate(BaseModel):
    status: QueryStatus

class QueryOut(BaseModel):
    id: int
    citizen_name: str
    address: str
    query_text: str
    query_type: QueryType
    status: QueryStatus
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True
