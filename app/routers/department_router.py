from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Department, Equipment, DepartmentEquipment, Factory
from app.database import get_db
from typing import List
from sqlalchemy.future import select
from app.schemas import DepartmentResponse, DepartmentCreateDepartment, DepartmentSearchResponse, \
    DepartmentDeepResponse, DepartmentUpdate

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


@department_router.get("/{department_id}", response_model=DepartmentDeepResponse, response_model_exclude_defaults=True)
async def search_department_by_id(department_id: int, depth: int = 0, db: AsyncSession = Depends(get_db)):
    query = select(Department).where(Department.id == department_id)
    result = await db.execute(query)
    department = result.scalars().first()

    if not department:
        raise HTTPException(status_code=404, detail=f"Department with id {department_id} not found")

    department_response = {
        "id": department.id,
        "name": department.name,
        "factory_id": department.factory_id,
        "equipments": []
    }

    if depth >= 1:
        query_factory = select(Factory).where(Factory.id == department.factory_id)
        result_factory = await db.execute(query_factory)
        factory = result_factory.scalars().first()

        if factory:
            department_response["factory"] = {
                "id": factory.id,
                "name": factory.name
            }

        query_equipments = select(Equipment).join(DepartmentEquipment).where(DepartmentEquipment.department_id == department.id)
        result_equipments = await db.execute(query_equipments)
        equipments = result_equipments.scalars().all()

        for equipment in equipments:
            department_response["equipments"].append({
                "id": equipment.id,
                "name": equipment.name
            })

    return department_response


@department_router.put("/{department_id}", response_model=DepartmentSearchResponse)
async def update_department(department_id: int, department_data: DepartmentUpdate, db: AsyncSession = Depends(get_db)):
    query = select(Department).where(Department.id == department_id)
    result = await db.execute(query)
    department = result.scalars().first()

    if not department:
        raise HTTPException(status_code=404, detail=f"Department with id {department_id} not found")

    if department_data.name is not None:
        department.name = department_data.name

    if department_data.factory_id is not None:
        query_factory = select(Factory).where(Factory.id == department_data.factory_id)
        result_factory = await db.execute(query_factory)
        factory = result_factory.scalars().first()

        if not factory:
            raise HTTPException(status_code=404, detail=f"Factory with id {department_data.factory_id} not found")

        department.factory_id = department_data.factory_id

    await db.commit()
    await db.refresh(department)

    return department