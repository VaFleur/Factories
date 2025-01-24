from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Equipment
from app.schemas import EquipmentResponse, EquipmentCreate
from app.database import get_db

equipment_router = APIRouter(prefix="/equipment", tags=["Equipment"])

@equipment_router.post("", response_model=EquipmentResponse)
async def create_equipment(equipment: EquipmentCreate, db: AsyncSession = Depends(get_db)):
    db_equipment = Equipment(name=equipment.name)
    db.add(db_equipment)
    await db.commit()
    await db.refresh(db_equipment)
    return db_equipment

