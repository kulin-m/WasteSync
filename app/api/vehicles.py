from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.vehicle import Vehicle
from app.models.depot import Depot
from app.schemas.vehicle import VehicleCreate, VehicleOut, DepotCreate, DepotOut

router = APIRouter(tags=["Vehicles & Depots"])

@router.get("/vehicles", response_model=List[VehicleOut])
async def list_vehicles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vehicle))
    return result.scalars().all()

@router.post("/vehicles", response_model=VehicleOut, status_code=status.HTTP_201_CREATED)
async def create_vehicle(v_in: VehicleCreate, db: AsyncSession = Depends(get_db)):
    vehicle = Vehicle(
        vehicle_number=v_in.vehicle_number,
        capacity=v_in.capacity,
        driver_id=v_in.driver_id,
        status=v_in.status
    )
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)
    return vehicle

@router.get("/depots", response_model=List[DepotOut])
async def list_depots(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Depot))
    return result.scalars().all()

@router.post("/depots", response_model=DepotOut, status_code=status.HTTP_201_CREATED)
async def create_depot(depot_in: DepotCreate, db: AsyncSession = Depends(get_db)):
    depot = Depot(
        name=depot_in.name,
        latitude=depot_in.latitude,
        longitude=depot_in.longitude,
        address=depot_in.address
    )
    db.add(depot)
    await db.commit()
    await db.refresh(depot)
    return depot
