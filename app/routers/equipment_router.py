from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Equipment, Department, DepartmentEquipment
from app.schemas import EquipmentResponse, EquipmentCreate, EquipmentSearchResponse
from app.database import get_db
from sqlalchemy.future import select

equipment_router = APIRouter(prefix="/equipments", tags=["Equipment"])

@equipment_router.post("", response_model=List[EquipmentResponse])
async def create_equipments(equipments_data: List[EquipmentCreate], db: AsyncSession = Depends(get_db)):
    created_equipments = []

    async with db.begin():
        for equipment_data in equipments_data:
            db_equipment = Equipment(name=equipment_data.name)
            db.add(db_equipment)
            await db.flush()

            for department_link in equipment_data.departments:
                query = select(Department).where(Department.id == department_link.department_id)
                result = await db.execute(query)
                department = result.scalars().first()

                if not department:
                    raise HTTPException(status_code=404, detail=f"Department with id {department_link.department_id} not found")

                db_relation = DepartmentEquipment(department_id=department_link.department_id, equipment_id=db_equipment.id)
                db.add(db_relation)

            created_equipments.append({
                "id": db_equipment.id,
                "name": db_equipment.name
            })

    await db.commit()
    return created_equipments

@equipment_router.get("/search", response_model=List[EquipmentSearchResponse])
async def search_equipments(search: str, db: AsyncSession = Depends(get_db)):
    query = select(Equipment).where(Equipment.name.ilike(f"%{search}%"))
    result = await db.execute(query)
    equipments = result.scalars().all()
    if not equipments:
        raise HTTPException(status_code=404, detail=f"Equipment {search} not found")
    return [{"id": e.id, "name": e.name} for e in equipments]