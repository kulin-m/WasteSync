from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.query import CitizenQuery, QueryType, QueryStatus
from app.schemas.query import QueryCreate, QueryOut, QueryStatusUpdate

router = APIRouter(prefix="/queries", tags=["Citizen & Driver Queries"])

@router.get("", response_model=List[QueryOut])
async def list_queries(query_type: Optional[QueryType] = None, status: Optional[QueryStatus] = None, db: AsyncSession = Depends(get_db)):
    stmt = select(CitizenQuery)
    if query_type:
        stmt = stmt.where(CitizenQuery.query_type == query_type)
    if status:
        stmt = stmt.where(CitizenQuery.status == status)
    result = await db.execute(stmt.order_by(CitizenQuery.created_at.desc()))
    return result.scalars().all()

@router.post("", response_model=QueryOut, status_code=status.HTTP_201_CREATED)
async def create_query(q_in: QueryCreate, db: AsyncSession = Depends(get_db)):
    query = CitizenQuery(
        citizen_name=q_in.citizen_name,
        address=q_in.address,
        query_text=q_in.query_text,
        query_type=q_in.query_type,
        latitude=q_in.latitude,
        longitude=q_in.longitude,
        status=QueryStatus.PENDING
    )
    db.add(query)
    await db.commit()
    await db.refresh(query)
    return query

@router.patch("/{query_id}/status", response_model=QueryOut)
async def update_query_status(query_id: int, status_in: QueryStatusUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CitizenQuery).where(CitizenQuery.id == query_id))
    query_obj = result.scalar_one_or_none()
    if not query_obj:
        raise HTTPException(status_code=404, detail="Query not found")
    
    query_obj.status = status_in.status
    await db.commit()
    await db.refresh(query_obj)
    return query_obj
