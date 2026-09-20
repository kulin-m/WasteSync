import enum
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, Float, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class QueryType(str, enum.Enum):
    CLEANLINESS_ISSUE = "cleanliness_issue"
    DUSTBIN_REQUEST = "dustbin_request"
    DRIVER_ISSUE = "driver_issue"

class QueryStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"

class CitizenQuery(Base):
    __tablename__ = "citizen_queries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    citizen_name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    query_type: Mapped[QueryType] = mapped_column(Enum(QueryType), default=QueryType.CLEANLINESS_ISSUE, nullable=False)
    status: Mapped[QueryStatus] = mapped_column(Enum(QueryStatus), default=QueryStatus.PENDING, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
