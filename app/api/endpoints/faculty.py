from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional
from app.api import deps
from app.db.session import get_db
from app.models import Faculty
from app.schemas import FacultyBase

router = APIRouter()

@router.get("/", response_model=list[FacultyBase])
async def list_faculty(skip: int = 0, limit: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    API endpoint lấy danh sách khoa với phân trang offset/limit.

    Hỗ trợ phân trang bằng offset/limit để tối ưu hiệu suất.

    Args:
        skip: Số bản ghi bỏ qua (offset)
        limit: Số lượng bản ghi tối đa trả về
        db: Session database async

    Returns:
        List[FacultyBase]: Danh sách các khoa
    """
    query = select(Faculty).order_by(Faculty.faculty_id.asc()).offset(skip)
    if limit is not None:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{faculty_id}", response_model=FacultyBase)
async def read_faculty(faculty_id: str, db: AsyncSession = Depends(get_db)):
    """Lấy thông tin khoa cụ thể."""
    result = await db.execute(select(Faculty).where(Faculty.faculty_id == faculty_id))
    faculty = result.scalars().first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Khoa không tồn tại")
    return faculty

@router.put("/{faculty_id}", response_model=FacultyBase)
async def update_faculty(faculty_id: str, data: FacultyBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Cập nhật khoa."""
    existing = await db.get(Faculty, faculty_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Khoa không tồn tại")
    
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

@router.post("/")
async def create_faculty(data: FacultyBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Tạo khoa mới."""
    obj = Faculty(**data.dict())
    db.add(obj)
    await db.commit()
    return obj

@router.delete("/{id}")
async def remove_faculty(id: str, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Xóa khoa theo ID."""
    existing = await db.get(Faculty, id)
    if not existing:
        raise HTTPException(status_code=404, detail="Khoa không tồn tại")
    await db.delete(existing)
    await db.commit()
    return {"message": f"Đã xóa khoa {id}"}
