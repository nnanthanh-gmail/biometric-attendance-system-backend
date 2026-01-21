from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.api import deps
from app.db.session import get_db
from app.models import Fingerprint, User
from app.schemas import FingerprintResponse, FingerprintCreate

router = APIRouter()

@router.get("/", response_model=list[FingerprintResponse])
async def read_fingerprints(skip: int = 0, limit: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """Lấy danh sách vân tay."""
    query = select(Fingerprint).offset(skip)
    if limit:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{finger_id}", response_model=FingerprintResponse)
async def read_fingerprint(finger_id: str, db: AsyncSession = Depends(get_db)):
    """Lấy vân tay theo ID."""
    result = await db.execute(select(Fingerprint).where(Fingerprint.finger_id == finger_id))
    fp = result.scalars().first()
    if not fp:
        raise HTTPException(status_code=404, detail="Fingerprint not found")
    return fp

@router.get("/user/{user_id}", response_model=list[FingerprintResponse])
async def read_fingerprints_by_user(user_id: str, skip: int = 0, limit: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    API endpoint lấy danh sách vân tay theo người dùng với phân trang offset/limit.

    Hỗ trợ phân trang bằng offset/limit để tối ưu hiệu suất.

    Args:
        user_id: ID người dùng
        skip: Số bản ghi bỏ qua (offset)
        limit: Số lượng bản ghi tối đa trả về
        db: Session database async

    Returns:
        List[FingerprintResponse]: Danh sách vân tay của người dùng
    """
    query = select(Fingerprint).where(Fingerprint.user_id == user_id).order_by(Fingerprint.finger_id.asc()).offset(skip)
    if limit:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=FingerprintResponse)
async def create_fingerprint(data: FingerprintCreate, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Tạo vân tay mới."""
    # Validate user exists
    if not await db.get(User, data.user_id):
        raise HTTPException(status_code=400, detail="User not found")
    
    obj = Fingerprint(**data.dict())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return FingerprintResponse(finger_id=obj.finger_id, user_id=obj.user_id)

@router.put("/{finger_id}", response_model=FingerprintResponse)
async def update_fingerprint(finger_id: str, data: FingerprintCreate, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Cập nhật vân tay."""
    existing = await db.get(Fingerprint, finger_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Fingerprint not found")
    
    # Validate user exists
    if not await db.get(User, data.user_id):
        raise HTTPException(status_code=400, detail="User not found")
    
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing, field, value)
    
    try:
        await db.commit()
        await db.refresh(existing)
        return FingerprintResponse(finger_id=existing.finger_id, user_id=existing.user_id)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi cập nhật: {str(e)}")

@router.delete("/{finger_id}")
async def delete_fingerprint(finger_id: str, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Xóa vân tay."""
    existing = await db.get(Fingerprint, finger_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Fingerprint not found")
    await db.delete(existing)
    await db.commit()
    return {"message": f"Đã xóa vân tay {finger_id}"}