from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Department, Equipment, DepartmentEquipment, Factory
from app.database import get_db
from typing import List
from sqlalchemy.future import select
from app.schemas import DepartmentResponse, DepartmentCreateDepartment, DepartmentSearchResponse

department_router = APIRouter(prefix="/departments", tags=["Departments"])

@department_router.post("", response_model=List[DepartmentResponse])
async def create_departments(departments_data: List[DepartmentCreateDepartment], db: AsyncSession = Depends(get_db)):
    created_departments = []

    async with db.begin():
        for department_data in departments_data:
            query = select(Factory).where(Factory.id == department_data.factory_id)
            result = await db.execute(query)
            factory = result.scalars().first()

            if not factory:
                raise HTTPException(status_code=404, detail=f"Factory with id {department_data.factory_id} not found")

            db_department = Department(name=department_data.name, factory_id=department_data.factory_id)
            db.add(db_department)
            await db.flush()

            created_equipments = []
            for equipment_data in department_data.equipments:
                db_equipment = Equipment(name=equipment_data.name)
                db.add(db_equipment)
                await db.flush()

                db_relation = DepartmentEquipment(department_id=db_department.id, equipment_id=db_equipment.id)
                db.add(db_relation)

                created_equipments.append({
                    "id": db_equipment.id,
                    "name": db_equipment.name
                })

            created_departments.append({
                "id": db_department.id,
                "name": db_department.name,
                "factory_id": department_data.factory_id,
                "equipments": created_equipments
            })

    await db.commit()
    return created_departments

@department_router.get("/search", response_model=List[DepartmentSearchResponse])
async def search_departments(search: str, db: AsyncSession = Depends(get_db)):
    query = select(Department).where(Department.name.ilike(f"%{search}%"))
    result = await db.execute(query)
    departments = result.scalars().all()
    if not departments:
        raise HTTPException(status_code=404, detail=f"Department {search} not found")
    return [{"id": d.id, "name": d.name, "factory_id": d.factory_id} for d in departments]
