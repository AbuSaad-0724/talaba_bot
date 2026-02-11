"""
Library Materials Database Models and API
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

Base = declarative_base()

# Database Model
class LibraryMaterial(Base):
    __tablename__ = "library_materials"
    
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(50), nullable=False, index=True)
    level = Column(String(20), nullable=False, index=True)
    material_type = Column(String(10), nullable=False)  # video, pdf, audio
    title = Column(String(200), nullable=False)
    duration = Column(String(50))  # "45 min" or "120 pages"
    file_url = Column(Text)
    description = Column(Text)
    file_size = Column(Integer)  # in bytes
    views_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer)  # admin user_id

# Pydantic Models for API
class MaterialCreate(BaseModel):
    subject: str
    level: str
    material_type: str
    title: str
    duration: Optional[str] = None
    file_url: Optional[str] = None
    description: Optional[str] = None
    file_size: Optional[int] = None

class MaterialUpdate(BaseModel):
    title: Optional[str] = None
    duration: Optional[str] = None
    file_url: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class MaterialResponse(BaseModel):
    id: int
    subject: str
    level: str
    material_type: str
    title: str
    duration: Optional[str]
    file_url: Optional[str]
    description: Optional[str]
    views_count: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class MaterialsList(BaseModel):
    total: int
    materials: List[MaterialResponse]

# Subject and Level mappings
SUBJECTS = {
    'mathematics': 'Matematika',
    'physics': 'Fizika',
    'chemistry': 'Kimyo',
    'english': 'Ingliz tili',
    'russian': 'Rus tili',
    'worldHistory': 'Jahon tarixi',
    'uzbekistanHistory': 'O\'zbekiston tarixi',
    'biology': 'Biologiya',
    'geography': 'Geografiya',
    'literature': 'Adabiyot',
    'programming': 'Dasturlash',
    'economics': 'Iqtisod'
}

LEVELS = {
    'beginner': 'Boshlang\'ich',
    'intermediate': 'O\'rta',
    'advanced': 'Yuqori/Oliy'
}
