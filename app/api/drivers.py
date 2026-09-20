from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserOut
from app.core.security import get_password_hash

router = APIRouter(prefix="/drivers", tags=["Drivers"])

@router.get("", response_model=List[UserOut])
async def list_drivers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.role == UserRole.DRIVER))
    return result.scalars().all()

@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_driver(driver_in: UserCreate, db: AsyncSession = Depends(get_db)):
    driver_in.role = UserRole.DRIVER
    result = await db.execute(select(User).where(User.email == driver_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Driver email already registered")
    
    driver = User(
        email=driver_in.email,
        hashed_password=get_password_hash(driver_in.password),
        name=driver_in.name,
        mobile=driver_in.mobile,
        address=driver_in.address,
        age=driver_in.age,
        gender=driver_in.gender,
        role=UserRole.DRIVER
    )
    db.add(driver)
    await db.commit()
    await db.refresh(driver)
    return driver
