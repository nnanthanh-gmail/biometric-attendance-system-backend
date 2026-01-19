from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.api import deps
from app.db.session import get_db
from app.models import Room
from app.schemas import RoomBase

router = APIRouter()

@router.get("/", response_model=list[RoomBase])
async def list_rooms(db: AsyncSession = Depends(get_db)):
    """Lấy danh sách phòng."""
    res = await db.execute(select(Room))
    return res.scalars().all()

@router.post("/")
async def create_room(data: RoomBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Tạo phòng mới."""
    obj = Room(**data.dict())
    db.add(obj)
    await db.commit()
    return obj
