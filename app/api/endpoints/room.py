from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional
from app.api import deps
from app.db.session import get_db
from app.models import Room
from app.schemas import RoomBase

router = APIRouter()

@router.get("/", response_model=list[RoomBase])
async def list_rooms(skip: int = 0, limit: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    API endpoint lấy danh sách phòng học với phân trang offset/limit.

    Hỗ trợ phân trang bằng offset/limit để tối ưu hiệu suất.

    Args:
        skip: Số bản ghi bỏ qua (offset)
        limit: Số lượng bản ghi tối đa trả về
        db: Session database async

    Returns:
        List[RoomBase]: Danh sách các phòng học
    """
    query = select(Room).order_by(Room.room_id.asc()).offset(skip)
    if limit is not None:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{room_id}", response_model=RoomBase)
async def read_room(room_id: str, db: AsyncSession = Depends(get_db)):
    """Lấy thông tin phòng cụ thể."""
    result = await db.execute(select(Room).where(Room.room_id == room_id))
    room = result.scalars().first()
    if not room:
        raise HTTPException(status_code=404, detail="Phòng không tồn tại")
    return room

@router.put("/{room_id}", response_model=RoomBase)
async def update_room(room_id: str, data: RoomBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Cập nhật phòng."""
    existing = await db.get(Room, room_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Phòng không tồn tại")
    
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
async def create_room(data: RoomBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Tạo phòng mới."""
    obj = Room(**data.dict())
    db.add(obj)
    await db.commit()
    return obj

@router.delete("/{room_id}")
async def delete_room(room_id: str, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Xóa phòng."""
    existing = await db.get(Room, room_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Phòng không tồn tại")
    await db.delete(existing)
    await db.commit()
    return {"message": f"Đã xóa phòng {room_id}"}
