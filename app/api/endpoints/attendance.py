from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api import deps
from app.db.session import get_db
from app.models import Attendance
from app.schemas import AttendanceBase

router = APIRouter()

@router.get("/", response_model=list[AttendanceBase])
async def read_attendance(db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Lấy nhật ký điểm danh."""
    result = await db.execute(select(Attendance).order_by(Attendance.attend_time.desc()))
    return result.scalars().all()

@router.post("/", response_model=AttendanceBase)
async def create_record(data: AttendanceBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Tạo bản ghi điểm danh thủ công."""
    obj = Attendance(**data.dict())
    db.add(obj)
    await db.commit()
    return obj
