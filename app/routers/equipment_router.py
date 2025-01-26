from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Equipment, Department, DepartmentEquipment, Factory
from app.schemas import EquipmentResponse, EquipmentCreate, EquipmentSearchResponse, EquipmentDeepResponse, \
    EquipmentUpdate
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


@equipment_router.get("/{equipment_id}", response_model=EquipmentDeepResponse, response_model_exclude_defaults=True)
async def search_equipment_by_id(equipment_id: int, depth: int = 0, db: AsyncSession = Depends(get_db)):
    query = select(Equipment).where(Equipment.id == equipment_id)
    result = await db.execute(query)
    equipment = result.scalars().first()

    if not equipment:
        raise HTTPException(status_code=404, detail=f"Equipment with id {equipment_id} not found")

    equipment_response = {
        "id": equipment.id,
        "name": equipment.name,
        "departments": []
    }

    if depth >= 1:
        query_departments = select(Department).join(
            DepartmentEquipment
        ).where(DepartmentEquipment.equipment_id == equipment.id)
        result_departments = await db.execute(query_departments)
        departments = result_departments.scalars().all()

        for department in departments:
            department_response = {
                "id": department.id,
                "name": department.name,
                "factory_id": department.factory_id
            }

            if depth >= 2:
                query_factory = select(Factory).where(Factory.id == department.factory_id)
                result_factory = await db.execute(query_factory)
                factory = result_factory.scalars().first()

                if factory:
                    department_response["factory"] = {
                        "id": factory.id,
                        "name": factory.name
                    }

            equipment_response["departments"].append(department_response)

    return equipment_response


@equipment_router.put("/{equipment_id}", response_model=EquipmentSearchResponse)
async def update_equipment(equipment_id: int, equipment_data: EquipmentUpdate, db: AsyncSession = Depends(get_db)):
    query = select(Equipment).where(Equipment.id == equipment_id)
    result = await db.execute(query)
    equipment = result.scalars().first()

    if not equipment:
        raise HTTPException(status_code=404, detail=f"Equipment with id {equipment_id} not found")

    if equipment_data.name is not None:
        equipment.name = equipment_data.name

    if equipment_data.departments is not None:
        query_remove_relations = DepartmentEquipment.__table__.delete().where(
            DepartmentEquipment.equipment_id == equipment.id
        )
        await db.execute(query_remove_relations)

        for department_link in equipment_data.departments:
            query_department = select(Department).where(Department.id == department_link.department_id)
            result_department = await db.execute(query_department)
            department = result_department.scalars().first()

            if not department:
                raise HTTPException(status_code=404,
                                    detail=f"Department with id {department_link.department_id} not found")

            db_relation = DepartmentEquipment(department_id=department.id, equipment_id=equipment.id)
            db.add(db_relation)

    await db.commit()
    await db.refresh(equipment)

    return equipment