from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional
from app.api import deps
from app.db.session import get_db
from app.models import Subject
from app.schemas import SubjectBase

router = APIRouter()

@router.get("/", response_model=list[SubjectBase])
async def list_subjects(skip: int = 0, limit: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    API endpoint lấy danh sách môn học với phân trang offset/limit.

    Hỗ trợ phân trang bằng offset/limit để tối ưu hiệu suất.

    Args:
        skip: Số bản ghi bỏ qua (offset)
        limit: Số lượng bản ghi tối đa trả về
        db: Session database async

    Returns:
        List[SubjectBase]: Danh sách các môn học
    """
    query = select(Subject).order_by(Subject.subject_id.asc()).offset(skip)
    if limit is not None:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{subject_id}", response_model=SubjectBase)
async def read_subject(subject_id: str, db: AsyncSession = Depends(get_db)):
    """Lấy thông tin môn học cụ thể."""
    result = await db.execute(select(Subject).where(Subject.subject_id == subject_id))
    subject = result.scalars().first()
    if not subject:
        raise HTTPException(status_code=404, detail="Môn học không tồn tại")
    return subject

@router.put("/{subject_id}", response_model=SubjectBase)
async def update_subject(subject_id: str, data: SubjectBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Cập nhật môn học."""
    existing = await db.get(Subject, subject_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Môn học không tồn tại")
    
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
async def create_subject(data: SubjectBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Tạo môn học mới."""
    obj = Subject(**data.dict())
    db.add(obj)
    await db.commit()
    return obj

@router.delete("/{subject_id}")
async def delete_subject(subject_id: str, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Xóa môn học."""
    existing = await db.get(Subject, subject_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Môn học không tồn tại")
    await db.delete(existing)
    await db.commit()
    return {"message": f"Đã xóa môn học {subject_id}"}
