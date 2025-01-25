from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Factory, Department, Equipment, DepartmentEquipment
from app.schemas import FactoryResponse, FactoryCreate, FactorySearchResponse
from app.database import get_db
from typing import List
from sqlalchemy.future import select

factory_router = APIRouter(prefix="/factories", tags=["Factories"])

@factory_router.post("", response_model=List[FactoryResponse])
async def create_factories(factories_data: List[FactoryCreate], db: AsyncSession = Depends(get_db)):
    created_factories = []

    async with db.begin():
        for factory_data in factories_data:
            db_factory = Factory(name=factory_data.name)
            db.add(db_factory)
            await db.flush()

            created_departments = []
            for department_data in factory_data.departments:
                db_department = Department(name=department_data.name, factory_id=db_factory.id)
                db.add(db_department)
                await db.flush()

                created_equipments = []
                for equipment_data in department_data.equipments:
                    db_equipment = Equipment(name=equipment_data.name)
                    db.add(db_equipment)
                    await db.flush()

                    db_relation = DepartmentEquipment(department_id=db_department.id,
                                                             equipment_id=db_equipment.id)
                    db.add(db_relation)

                    created_equipments.append({
                        "id": db_equipment.id,
                        "name": db_equipment.name
                    })

                created_departments.append({
                    "id": db_department.id,
                    "name": db_department.name,
                    "factory_id": db_factory.id,
                    "equipments": created_equipments
                })

            created_factories.append({
                "id": db_factory.id,
                "name": db_factory.name,
                "departments": created_departments
            })

    await db.commit()
    return created_factories

@factory_router.get("/search", response_model=List[FactorySearchResponse])
async def search_factories(search: str, db: AsyncSession = Depends(get_db)):
    query = select(Factory).where(Factory.name.ilike(f"%{search}%"))
    result = await db.execute(query)
    factories = result.scalars().all()
    if not factories:
        raise HTTPException(status_code=404, detail=f"Factory {search} not found")
    return [{"id": f.id, "name": f.name} for f in factories]
