from pydantic import BaseModel
from typing import List

class EquipmentCreate(BaseModel):
    name: str

class EquipmentResponse(BaseModel):
    id: int
    name: str

class DepartmentCreate(BaseModel):
    name: str
    equipments: List[EquipmentCreate] = []

class DepartmentResponse(BaseModel):
    id: int
    name: str
    equipments: List[EquipmentResponse]

class FactoryCreate(BaseModel):
    name: str
    departments: List[DepartmentCreate] = []

class FactoryResponse(BaseModel):
    id: int
    name: str
    departments: List[DepartmentResponse]
