from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional
from datetime import date
from app.api import deps
from app.db.session import get_db
from app.models import Schedule, Subject, Room, User, ClassModel
from app.schemas import ScheduleBase

router = APIRouter()

@router.get("/", response_model=list[ScheduleBase])
async def get_schedules(skip: int = 0, limit: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """Lấy danh sách lịch trình."""
    query = select(Schedule).order_by(Schedule.schedule_id.asc()).offset(skip)
    if limit is not None:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{schedule_id}", response_model=ScheduleBase)
async def read_schedule(schedule_id: int, db: AsyncSession = Depends(get_db)):
    """Lấy thông tin lịch trình cụ thể."""
    result = await db.execute(select(Schedule).where(Schedule.schedule_id == schedule_id))
    schedule = result.scalars().first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Lịch trình không tồn tại")
    return schedule

@router.put("/{schedule_id}", response_model=ScheduleBase)
async def update_schedule(schedule_id: int, data: ScheduleBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Cập nhật lịch trình."""
    existing = await db.get(Schedule, schedule_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Lịch trình không tồn tại")
    
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
async def add_schedule(data: ScheduleBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Tạo lịch trình mới."""
    # Validate FK
    if not await db.get(Subject, data.subject_id):
        raise HTTPException(status_code=400, detail="Môn học không tồn tại")
    if not await db.get(Room, data.room_id):
        raise HTTPException(status_code=400, detail="Phòng không tồn tại")
    if not await db.get(User, data.lecturer_id):
        raise HTTPException(status_code=400, detail="Giảng viên không tồn tại")
    if not await db.get(ClassModel, data.class_id):
        raise HTTPException(status_code=400, detail="Lớp không tồn tại")
    
    obj = Schedule(**data.dict())
    db.add(obj)
    await db.commit()
    return obj

@router.delete("/{id}")
async def delete_schedule(id: int, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Xóa lịch trình theo ID."""
    existing = await db.get(Schedule, id)
    if not existing:
        raise HTTPException(status_code=404, detail="Lịch trình không tồn tại")
    await db.delete(existing)
    await db.commit()
    return {"message": f"Đã xóa lịch trình {id}"}

@router.get("/lecturer/{lecturer_id}", response_model=list[ScheduleBase])
async def get_schedules_by_lecturer(lecturer_id: str, db: AsyncSession = Depends(get_db)):
    """Lấy danh sách lịch trình theo giảng viên."""
    query = select(Schedule).where(Schedule.lecturer_id == lecturer_id).order_by(Schedule.learn_date, Schedule.start_period)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/class/{class_id}", response_model=list[ScheduleBase])
async def get_schedules_by_class(class_id: str, db: AsyncSession = Depends(get_db)):
    """Lấy danh sách lịch trình theo lớp."""
    query = select(Schedule).where(Schedule.class_id == class_id).order_by(Schedule.learn_date, Schedule.start_period)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/date/{learn_date}", response_model=list[ScheduleBase])
async def get_schedules_by_date(learn_date: date, db: AsyncSession = Depends(get_db)):
    """Lấy danh sách lịch trình theo ngày."""
    query = select(Schedule).where(Schedule.learn_date == learn_date).order_by(Schedule.start_period)
    result = await db.execute(query)
    return result.scalars().all()
