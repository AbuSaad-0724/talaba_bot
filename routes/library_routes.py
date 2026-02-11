"""
Library API Routes
"""
import os
import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime

from models.library_models import (
    LibraryMaterial, MaterialCreate, MaterialUpdate, 
    MaterialResponse, MaterialsList, SUBJECTS, LEVELS
)
from database import get_db

router = APIRouter(prefix="/api/library", tags=["library"])
logger = logging.getLogger(__name__)

# Upload directory
UPLOAD_DIR = "uploads/library"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ============================================
# GET MATERIALS
# ============================================

@router.get("/materials", response_model=MaterialsList)
async def get_materials(
    subject: Optional[str] = None,
    level: Optional[str] = None,
    material_type: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all materials with optional filters"""
    try:
        query = db.query(LibraryMaterial).filter(LibraryMaterial.is_active == True)
        
        if subject:
            query = query.filter(LibraryMaterial.subject == subject)
        if level:
            query = query.filter(LibraryMaterial.level == level)
        if material_type:
            query = query.filter(LibraryMaterial.material_type == material_type)
        if search:
            query = query.filter(LibraryMaterial.title.ilike(f"%{search}%"))
        
        total = query.count()
        materials = query.order_by(LibraryMaterial.created_at.desc()).offset(skip).limit(limit).all()
        
        return MaterialsList(total=total, materials=materials)
    except Exception as e:
        logger.error(f"Error getting materials: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/materials/{material_id}", response_model=MaterialResponse)
async def get_material(material_id: int, db: Session = Depends(get_db)):
    """Get single material by ID"""
    material = db.query(LibraryMaterial).filter(LibraryMaterial.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    # Increment views
    material.views_count += 1
    db.commit()
    
    return material

@router.get("/subjects")
async def get_subjects():
    """Get all available subjects"""
    return {"subjects": SUBJECTS}

@router.get("/levels")
async def get_levels():
    """Get all available levels"""
    return {"levels": LEVELS}

@router.get("/stats/{subject}")
async def get_subject_stats(subject: str, db: Session = Depends(get_db)):
    """Get statistics for a subject"""
    try:
        total_materials = db.query(LibraryMaterial).filter(
            and_(
                LibraryMaterial.subject == subject,
                LibraryMaterial.is_active == True
            )
        ).count()
        
        video_count = db.query(LibraryMaterial).filter(
            and_(
                LibraryMaterial.subject == subject,
                LibraryMaterial.material_type == 'video',
                LibraryMaterial.is_active == True
            )
        ).count()
        
        pdf_count = db.query(LibraryMaterial).filter(
            and_(
                LibraryMaterial.subject == subject,
                LibraryMaterial.material_type == 'pdf',
                LibraryMaterial.is_active == True
            )
        ).count()
        
        audio_count = db.query(LibraryMaterial).filter(
            and_(
                LibraryMaterial.subject == subject,
                LibraryMaterial.material_type == 'audio',
                LibraryMaterial.is_active == True
            )
        ).count()
        
        return {
            "subject": subject,
            "total_materials": total_materials,
            "video_count": video_count,
            "pdf_count": pdf_count,
            "audio_count": audio_count
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# CREATE MATERIAL (ADMIN)
# ============================================

@router.post("/materials", response_model=MaterialResponse)
async def create_material(
    material: MaterialCreate,
    user_id: int,  # From Telegram auth
    db: Session = Depends(get_db)
):
    """Create new material (Admin only)"""
    try:
        # Validate subject and level
        if material.subject not in SUBJECTS:
            raise HTTPException(status_code=400, detail="Invalid subject")
        if material.level not in LEVELS:
            raise HTTPException(status_code=400, detail="Invalid level")
        if material.material_type not in ['video', 'pdf', 'audio']:
            raise HTTPException(status_code=400, detail="Invalid material type")
        
        new_material = LibraryMaterial(
            subject=material.subject,
            level=material.level,
            material_type=material.material_type,
            title=material.title,
            duration=material.duration,
            file_url=material.file_url,
            description=material.description,
            file_size=material.file_size,
            created_by=user_id
        )
        
        db.add(new_material)
        db.commit()
        db.refresh(new_material)
        
        logger.info(f"Material created: {new_material.id} by user {user_id}")
        return new_material
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating material: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# UPDATE MATERIAL (ADMIN)
# ============================================

@router.put("/materials/{material_id}", response_model=MaterialResponse)
async def update_material(
    material_id: int,
    material_update: MaterialUpdate,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Update material (Admin only)"""
    material = db.query(LibraryMaterial).filter(LibraryMaterial.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    try:
        update_data = material_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(material, key, value)
        
        material.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(material)
        
        logger.info(f"Material updated: {material_id} by user {user_id}")
        return material
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating material: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# DELETE MATERIAL (ADMIN)
# ============================================

@router.delete("/materials/{material_id}")
async def delete_material(
    material_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Soft delete material (Admin only)"""
    material = db.query(LibraryMaterial).filter(LibraryMaterial.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    try:
        material.is_active = False
        material.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Material deleted: {material_id} by user {user_id}")
        return {"message": "Material deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting material: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# FILE UPLOAD
# ============================================

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user_id: int = None
):
    """Upload file (video, audio, pdf)"""
    try:
        # Validate file type
        allowed_types = {
            'video': ['video/mp4', 'video/mpeg', 'video/quicktime'],
            'audio': ['audio/mpeg', 'audio/wav', 'audio/mp3'],
            'pdf': ['application/pdf']
        }
        
        file_type = None
        for type_name, mime_types in allowed_types.items():
            if file.content_type in mime_types:
                file_type = type_name
                break
        
        if not file_type:
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        file_size = len(content)
        file_url = f"/uploads/library/{filename}"
        
        logger.info(f"File uploaded: {filename} by user {user_id}")
        
        return {
            "filename": filename,
            "file_url": file_url,
            "file_size": file_size,
            "file_type": file_type
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))
