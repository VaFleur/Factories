from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Department
from app.schemas import DepartmentResponse, DepartmentCreate
from app.database import get_db

department_router = APIRouter(prefix="/departments", tags=["Departments"])

@department_router.post("", response_model=DepartmentResponse)
async def create_department(department: DepartmentCreate, db: AsyncSession = Depends(get_db)):
    db_department = Department(name=department.name)
    db.add(db_department)
    await db.commit()
    await db.refresh(db_department)
    return db_department

