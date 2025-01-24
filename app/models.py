from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Factory(Base):
    __tablename__ = "factories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    departments = relationship("FactoryDepartment", back_populates="factory")

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    factories = relationship("FactoryDepartment", back_populates="department")
    equipments = relationship("DepartmentEquipment", back_populates="department")

class Equipment(Base):
    __tablename__ = "equipment"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    departments = relationship("DepartmentEquipment", back_populates="equipment")

class FactoryDepartment(Base):
    __tablename__ = "factory_department"
    factory_id = Column(Integer, ForeignKey("factories.id"), primary_key=True)
    department_id = Column(Integer, ForeignKey("departments.id"), primary_key=True)
    factory = relationship("Factory", back_populates="departments")
    department = relationship("Department", back_populates="factories")

class DepartmentEquipment(Base):
    __tablename__ = "department_equipment"
    department_id = Column(Integer, ForeignKey("departments.id"), primary_key=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), primary_key=True)
    department = relationship("Department", back_populates="equipments")
    equipment = relationship("Equipment", back_populates="departments")
