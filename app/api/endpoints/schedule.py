from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.api import deps
from app.db.session import get_db
from app.models import Schedule
from app.schemas import ScheduleBase

router = APIRouter()

@router.get("/", response_model=list[ScheduleBase])
async def get_schedules(db: AsyncSession = Depends(get_db)):
    """Lấy danh sách lịch trình."""
    res = await db.execute(select(Schedule))
    return res.scalars().all()

@router.post("/")
async def add_schedule(data: ScheduleBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Tạo lịch trình mới."""
    obj = Schedule(**data.dict())
    db.add(obj)
    await db.commit()
    return obj

@router.delete("/{id}")
async def delete_schedule(id: int, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Xóa lịch trình theo ID."""
    await db.execute(delete(Schedule).where(Schedule.schedule_id == id))
    await db.commit()
    return {"msg": "Deleted"}
