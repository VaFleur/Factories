from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Factory, Department, Equipment, DepartmentEquipment
from app.schemas import FactoryResponse, FactoryCreate, FactorySearchResponse, FactoryDeepResponse, FactoryUpdate
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


@factory_router.get("/{factory_id}", response_model=FactoryDeepResponse, response_model_exclude_defaults=True)
async def search_factory_by_id(factory_id: int, depth: int = 0, db: AsyncSession = Depends(get_db)):
    query = select(Factory).where(Factory.id == factory_id)
    result = await db.execute(query)
    factory = result.scalars().first()

    if not factory:
        raise HTTPException(status_code=404, detail=f"Factory with id {factory_id} not found")

    factory_response = {
        "id": factory.id,
        "name": factory.name,
        "departments": []
    }

    if depth >= 1:
        query_departments = select(Department).where(Department.factory_id == factory_id)
        result_departments = await db.execute(query_departments)
        departments = result_departments.scalars().all()

        for department in departments:
            department_response = {
                "id": department.id,
                "name": department.name,
                "factory_id": department.factory_id,
                "equipments": []
            }

            if depth >= 2:
                query_equipments = select(Equipment).join(DepartmentEquipment).where(DepartmentEquipment.department_id == department.id)
                result_equipments = await db.execute(query_equipments)
                equipments = result_equipments.scalars().all()

                for equipment in equipments:
                    department_response["equipments"].append({
                        "id": equipment.id,
                        "name": equipment.name
                    })

            factory_response["departments"].append(department_response)

    return factory_response


@factory_router.put("/{factory_id}", response_model=FactorySearchResponse)
async def update_factory(factory_id: int, factory_data: FactoryUpdate, db: AsyncSession = Depends(get_db)):
    query = select(Factory).where(Factory.id == factory_id)
    result = await db.execute(query)
    factory = result.scalars().first()

    if not factory:
        raise HTTPException(status_code=404, detail=f"Factory with id {factory_id} not found")

    if factory_data.name is not None:
        factory.name = factory_data.name

    await db.commit()
    await db.refresh(factory)

    return factory


@factory_router.delete("/{factory_id}")
async def delete_factory(factory_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Factory).where(Factory.id == factory_id)
    result = await db.execute(query)
    factory = result.scalars().first()

    if not factory:
        raise HTTPException(status_code=404, detail=f"Factory with id {factory_id} not found")

    await db.execute(delete(Factory).where(Factory.id == factory_id))
    await db.commit()

    return {"message": f"Factory with id {factory_id} successfully deleted"}