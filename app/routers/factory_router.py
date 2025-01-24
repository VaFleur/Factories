from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Factory
from app.schemas import FactoryResponse, FactoryCreate
from app.database import get_db

factory_router = APIRouter(prefix="/factories", tags=["Factories"])

@factory_router.post("", response_model=FactoryResponse)
async def create_factory(factory: FactoryCreate, db: AsyncSession = Depends(get_db)):
    db_factory = Factory(name=factory.name)
    db.add(db_factory)
    await db.commit()
    await db.refresh(db_factory)
    return db_factory

