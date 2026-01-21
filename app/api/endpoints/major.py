from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.api import deps
from app.db.session import get_db
from app.models import Major, Faculty
from app.schemas import MajorResponse, MajorBase

router = APIRouter()

@router.get("/", response_model=list[MajorResponse])
async def read_majors(skip: int = 0, limit: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """Lấy danh sách chuyên ngành."""
    query = select(Major).offset(skip)
    if limit:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{major_id}", response_model=MajorResponse)
async def read_major(major_id: str, db: AsyncSession = Depends(get_db)):
    """Lấy chuyên ngành theo ID."""
    result = await db.execute(select(Major).where(Major.major_id == major_id))
    major = result.scalars().first()
    if not major:
        raise HTTPException(status_code=404, detail="Major not found")
    return major

@router.get("/faculty/{faculty_id}", response_model=list[MajorResponse])
async def read_majors_by_faculty(faculty_id: str, skip: int = 0, limit: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    API endpoint lấy danh sách chuyên ngành theo khoa với phân trang offset/limit.

    Hỗ trợ phân trang bằng offset/limit để tối ưu hiệu suất.

    Args:
        faculty_id: ID khoa
        skip: Số bản ghi bỏ qua (offset)
        limit: Số lượng bản ghi tối đa trả về
        db: Session database async

    Returns:
        List[MajorResponse]: Danh sách chuyên ngành của khoa
    """
    query = select(Major).where(Major.faculty_id == faculty_id).order_by(Major.major_id.asc()).offset(skip)
    if limit:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=MajorResponse)
async def create_major(data: MajorBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Tạo chuyên ngành mới."""
    # Validate faculty exists
    if not await db.get(Faculty, data.faculty_id):
        raise HTTPException(status_code=400, detail="Faculty not found")
    
    obj = Major(**data.dict())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

@router.put("/{major_id}", response_model=MajorResponse)
async def update_major(major_id: str, data: MajorBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Cập nhật chuyên ngành."""
    existing = await db.get(Major, major_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Major not found")
    
    # Validate faculty exists
    if not await db.get(Faculty, data.faculty_id):
        raise HTTPException(status_code=400, detail="Faculty not found")
    
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

@router.delete("/{major_id}")
async def delete_major(major_id: str, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Xóa chuyên ngành."""
    existing = await db.get(Major, major_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Major not found")
    await db.delete(existing)
    await db.commit()
    return {"message": f"Đã xóa chuyên ngành {major_id}"}