from pydantic import BaseModel
from typing import List, Optional


# Schemas for /equipments
class DepartmentLink(BaseModel):
    department_id: Optional[int] = None

class EquipmentCreate(BaseModel):
    name: str
    departments: Optional[List[DepartmentLink]] = []

class EquipmentSearchResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    departments: Optional[List[DepartmentLink]] = None

# Schemas for /departments
class EquipmentCreateDepartment(BaseModel):
    name: str

class DepartmentCreateDepartment(BaseModel):
    name: str
    factory_id: Optional[int] = None
    equipments: List[EquipmentCreateDepartment] = []

class EquipmentResponse(BaseModel):
    id: int
    name: str

class DepartmentResponse(BaseModel):
    id: int
    name: str
    factory_id: Optional[int] = None
    equipments: Optional[List[EquipmentResponse]] = None

class DepartmentSearchResponse(BaseModel):
    id: int
    name: str
    factory_id: Optional[int] = None

    class Config:
        orm_mode = True

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    factory_id: Optional[int] = None

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

    class Config:
        orm_mode = True

class FactoryUpdate(BaseModel):
    name: Optional[str] = None

# Schemas for search
class SearchRequest(BaseModel):
    search: str

# Schemas for deep search response
class EquipmentToDepartmentToFactoryDeepResponse(BaseModel):
    id: int
    name: str
    factory_id: int
    factory: Optional[FactorySearchResponse] = None

class EquipmentDeepResponse(BaseModel):
    id: int
    name: str
    departments: List[EquipmentToDepartmentToFactoryDeepResponse] = []

class DepartmentDeepResponse(BaseModel):
    id: int
    name: str
    factory_id: int
    factory: Optional[FactorySearchResponse] = None
    equipments: List[EquipmentSearchResponse] = []

class FactoryDeepResponse(BaseModel):
    id: int
    name: str
    departments: List[DepartmentDeepResponse] = []


