from pydantic import BaseModel
from typing import List

# Schemas for /equipments
class DepartmentLink(BaseModel):
    department_id: int

class EquipmentCreate(BaseModel):
    name: str
    departments: List[DepartmentLink] = []

class EquipmentSearchResponse(BaseModel):
    id: int
    name: str

# Schemas for /departments
class EquipmentCreateDepartment(BaseModel):
    name: str

class DepartmentCreateDepartment(BaseModel):
    name: str
    factory_id: int
    equipments: List[EquipmentCreateDepartment] = []

class EquipmentResponse(BaseModel):
    id: int
    name: str

class DepartmentResponse(BaseModel):
    id: int
    name: str
    factory_id: int
    equipments: List[EquipmentResponse]

class DepartmentSearchResponse(BaseModel):
    id: int
    name: str
    factory_id: int

# Schemas for /factories
class EquipmentCreateFactory(BaseModel):
    name: str

class DepartmentCreateFactory(BaseModel):
    name: str
    equipments: List[EquipmentCreateFactory] = []

class FactoryCreate(BaseModel):
    name: str
    departments: List[DepartmentCreateFactory] = []

class FactoryResponse(BaseModel):
    id: int
    name: str
    departments: List[DepartmentResponse]

class FactorySearchResponse(BaseModel):
    id: int
    name: str

# Schemas for search
class SearchRequest(BaseModel):
    search: str
