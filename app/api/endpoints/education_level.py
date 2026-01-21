from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.api import deps
from app.db.session import get_db
from app.models import EducationLevel
from app.schemas import EducationLevelBase, EducationLevelResponse

router = APIRouter()

@router.get("/", response_model=list[EducationLevelResponse])
async def read_education_levels(skip: int = 0, limit: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """Lấy danh sách cấp độ giáo dục."""
    query = select(EducationLevel).offset(skip)
    if limit:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{edu_level_id}", response_model=EducationLevelResponse)
async def read_education_level(edu_level_id: str, db: AsyncSession = Depends(get_db)):
    """Lấy cấp độ giáo dục theo ID."""
    result = await db.execute(select(EducationLevel).where(EducationLevel.edu_level_id == edu_level_id))
    level = result.scalars().first()
    if not level:
        raise HTTPException(status_code=404, detail="Education level not found")
    return level

@router.post("/", response_model=EducationLevelResponse)
async def create_education_level(data: EducationLevelBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Tạo cấp độ giáo dục mới."""
    obj = EducationLevel(**data.dict())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

@router.put("/{edu_level_id}", response_model=EducationLevelResponse)
async def update_education_level(edu_level_id: str, data: EducationLevelBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Cập nhật cấp độ giáo dục."""
    existing = await db.get(EducationLevel, edu_level_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Education level not found")
    
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing, field, value)
    
    try:
        await db.commit()
        await db.refresh(existing)
        return existing
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi cập nhật: {str(e)}")

@router.delete("/{edu_level_id}")
async def delete_education_level(edu_level_id: str, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Xóa cấp độ giáo dục."""
    existing = await db.get(EducationLevel, edu_level_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Education level not found")
    await db.delete(existing)
    await db.commit()
    return {"message": f"Đã xóa cấp độ giáo dục {edu_level_id}"}