from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Optional
from app.api import deps
from app.db.session import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, UserBase

router = APIRouter()

@router.get("/", response_model=list[UserBase])
async def read_users(skip: int = 0, limit: Optional[int] = None, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Lấy danh sách người dùng với phân trang tùy chọn."""
    query = select(User).offset(skip)
    if limit is not None:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=UserBase)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Tạo người dùng mới với thông tin được cung cấp."""
    new_user = User(**user_in.dict())
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=400, detail="ID người dùng đã tồn tại")

@router.put("/{user_id}", response_model=UserBase)
async def update_user(user_id: str, user_in: UserCreate, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Cập nhật thông tin của người dùng hiện có."""
    q = update(User).where(User.user_id == user_id).values(**user_in.dict(exclude_unset=True))
    await db.execute(q)
    await db.commit()
    return await db.get(User, user_id)

@router.delete("/{user_id}")
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Xóa người dùng khỏi hệ thống."""
    query = delete(User).where(User.user_id == user_id)
    await db.execute(query)
    await db.commit()
    return {"status": "success", "message": f"Đã xóa người dùng {user_id}"}
