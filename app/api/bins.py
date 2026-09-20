from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.bin import Bin
from app.schemas.bin import BinCreate, BinOut, BinUpdateTelemetry

router = APIRouter(prefix="/bins", tags=["Bins"])

@router.get("", response_model=List[BinOut])
async def list_bins(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Bin))
    return result.scalars().all()

@router.post("", response_model=BinOut, status_code=status.HTTP_201_CREATED)
async def create_bin(bin_in: BinCreate, db: AsyncSession = Depends(get_db)):
    bin_obj = Bin(
        latitude=bin_in.latitude,
        longitude=bin_in.longitude,
        capacity=bin_in.capacity,
        height=bin_in.height,
        address=bin_in.address,
        current_garbage_height=0.0
    )
    db.add(bin_obj)
    await db.commit()
    await db.refresh(bin_obj)
    return bin_obj

@router.patch("/{bin_id}/telemetry", response_model=BinOut)
async def update_bin_telemetry(bin_id: int, telemetry: BinUpdateTelemetry, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Bin).where(Bin.id == bin_id))
    bin_obj = result.scalar_one_or_none()
    if not bin_obj:
        raise HTTPException(status_code=404, detail="Bin not found")
    
    bin_obj.current_garbage_height = telemetry.current_garbage_height
    await db.commit()
    await db.refresh(bin_obj)
    return bin_obj

@router.post("/{bin_id}/empty", response_model=BinOut)
async def empty_bin(bin_id: int, db: AsyncSession = Depends(get_db)):
    """Driver action: Empties the bin during collection route."""
    result = await db.execute(select(Bin).where(Bin.id == bin_id))
    bin_obj = result.scalar_one_or_none()
    if not bin_obj:
        raise HTTPException(status_code=404, detail="Bin not found")
    
    bin_obj.current_garbage_height = 0.0
    await db.commit()
    await db.refresh(bin_obj)
    return bin_obj

@router.delete("/{bin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bin(bin_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Bin).where(Bin.id == bin_id))
    bin_obj = result.scalar_one_or_none()
    if bin_obj:
        await db.delete(bin_obj)
        await db.commit()
