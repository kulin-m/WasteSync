import enum
from datetime import datetime, timezone
from sqlalchemy import String, Float, Enum, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class BinStatus(str, enum.Enum):
    UNDERFILLED = "underfilled"   # <= 20%
    NORMAL = "normal"             # 21-69%
    OVERFILLED = "overfilled"     # >= 70%

class Bin(Base):
    __tablename__ = "bins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    capacity: Mapped[float] = mapped_column(Float, nullable=False)  # in Liters or units
    height: Mapped[float] = mapped_column(Float, nullable=False)    # Total height in cm
    current_garbage_height: Mapped[float] = mapped_column(Float, default=0.0) # Current garbage height in cm
    address: Mapped[str] = mapped_column(String(500), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @property
    def fill_percentage(self) -> float:
        if self.height <= 0:
            return 0.0
        return min(100.0, max(0.0, (self.current_garbage_height / self.height) * 100.0))

    @property
    def status(self) -> BinStatus:
        perc = self.fill_percentage
        if perc >= 70.0:
            return BinStatus.OVERFILLED
        elif perc <= 20.0:
            return BinStatus.UNDERFILLED
        return BinStatus.NORMAL
