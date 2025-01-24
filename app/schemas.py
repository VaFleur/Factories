from pydantic import BaseModel


class FactoryCreate(BaseModel):
    name: str

class DepartmentCreate(BaseModel):
    name: str

class EquipmentCreate(BaseModel):
    name: str

class FactoryResponse(BaseModel):
    id: int
    name: str

class DepartmentResponse(BaseModel):
    id: int
    name: str

class EquipmentResponse(BaseModel):
    id: int
    name: str