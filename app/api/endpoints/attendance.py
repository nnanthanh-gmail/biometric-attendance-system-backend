"""
Endpoints quản lý điểm danh.

Cung cấp CRUD operations cho attendance records, bao gồm tạo, đọc, cập nhật và xóa bản ghi điểm danh.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.api import deps
from app.db.session import get_db
from app.models import Attendance, Schedule, User
from app.schemas import AttendanceBase

router = APIRouter()

@router.get("/", response_model=list[AttendanceBase])
async def read_attendance(skip: int = 0, limit: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    Lấy danh sách bản ghi điểm danh với pagination.

    Args:
        skip: Số bản ghi bỏ qua.
        limit: Số bản ghi tối đa trả về.
        db: Database session.

    Returns:
        Danh sách các AttendanceBase objects.
    """
    query = select(Attendance).order_by(Attendance.time.desc()).offset(skip)
    if limit is not None:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{attendance_id}", response_model=AttendanceBase)
async def read_attendance_record(attendance_id: int, db: AsyncSession = Depends(get_db)):
    """
    Lấy bản ghi điểm danh cụ thể theo ID.

    Args:
        attendance_id: ID duy nhất của bản ghi điểm danh.
        db: Database session.

    Returns:
        AttendanceBase object.

    Raises:
        HTTPException: Nếu bản ghi không tồn tại.
    """
    result = await db.execute(select(Attendance).where(Attendance.id == attendance_id))
    record = result.scalars().first()
    if not record:
        raise HTTPException(status_code=404, detail="Bản ghi điểm danh không tồn tại")
    return record

@router.put("/{attendance_id}", response_model=AttendanceBase)
async def update_attendance(attendance_id: int, data: AttendanceBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """
    Cập nhật bản ghi điểm danh. Yêu cầu admin authentication.

    Args:
        attendance_id: ID của bản ghi cần cập nhật.
        data: Dữ liệu cập nhật.
        db: Database session.
        _: Admin authentication dependency.

    Returns:
        AttendanceBase object đã cập nhật.

    Raises:
        HTTPException: Nếu bản ghi không tồn tại hoặc cập nhật thất bại.
    """
    existing = await db.get(Attendance, attendance_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Bản ghi điểm danh không tồn tại")
    
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

@router.post("/", response_model=AttendanceBase)
async def create_record(data: AttendanceBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """
    Tạo bản ghi điểm danh mới. Yêu cầu admin authentication.

    Args:
        data: Dữ liệu tạo bản ghi điểm danh.
        db: Database session.
        _: Admin authentication dependency.

    Returns:
        AttendanceBase object đã tạo.

    Raises:
        HTTPException: Nếu schedule hoặc user không tồn tại.
    """
    # Validate FK
    if not await db.get(Schedule, data.schedule_id):
        raise HTTPException(status_code=400, detail="Lịch trình không tồn tại")
    if not await db.get(User, data.user_id):
        raise HTTPException(status_code=400, detail="Người dùng không tồn tại")
    
    obj = Attendance(**data.dict())
    db.add(obj)
    await db.commit()
    return obj

@router.delete("/{attendance_id}")
async def delete_attendance(attendance_id: int, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """
    Xóa bản ghi điểm danh. Yêu cầu admin authentication.

    Args:
        attendance_id: ID của bản ghi cần xóa.
        db: Database session.
        _: Admin authentication dependency.

    Returns:
        Thông báo thành công.

    Raises:
        HTTPException: Nếu bản ghi không tồn tại.
    """
    existing = await db.get(Attendance, attendance_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Bản ghi điểm danh không tồn tại")
    await db.delete(existing)
    await db.commit()
    return {"message": f"Đã xóa bản ghi điểm danh {attendance_id}"}

@router.get("/schedule/{schedule_id}", response_model=list[AttendanceBase])
async def get_attendance_by_schedule(schedule_id: int, db: AsyncSession = Depends(get_db)):
    """
    Lấy danh sách bản ghi điểm danh theo schedule ID.

    Args:
        schedule_id: ID của lịch trình.
        db: Database session.

    Returns:
        Danh sách các AttendanceBase objects.
    """
    query = select(Attendance).where(Attendance.schedule_id == schedule_id).order_by(Attendance.time.desc())
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/user/{user_id}", response_model=list[AttendanceBase])
async def get_attendance_by_user(
    user_id: str, 
    skip: int = 0, 
    limit: Optional[int] = None, 
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy lịch sử điểm danh của một user với pagination.

    Args:
        user_id: ID của user.
        skip: Số bản ghi bỏ qua.
        limit: Số bản ghi tối đa trả về.
        db: Database session.

    Returns:
        Danh sách các AttendanceBase objects.
    """
    query = select(Attendance).where(Attendance.user_id == user_id).order_by(Attendance.time.desc()).offset(skip)
    if limit:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
