from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Optional
from app.api import deps
from app.db.session import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, UserBase, UserUpdate

router = APIRouter()

@router.get("/", response_model=list[UserBase])
async def read_users(skip: int = 0, limit: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """Lấy danh sách người dùng với phân trang."""
    query = select(User).order_by(User.user_id.asc()).offset(skip)
    if limit is not None:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{user_id}", response_model=UserBase)
async def read_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """Lấy thông tin của một người dùng cụ thể."""
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    return user

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
async def update_user(user_id: str, user_in: UserUpdate, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Cập nhật thông tin của người dùng hiện có."""
    # Kiểm tra xem user có tồn tại không
    existing_user = await db.get(User, user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    
    update_data = user_in.dict(exclude_unset=True)
    
    # Nếu có user_id mới, thực hiện migrate user
    if 'user_id' in update_data and update_data['user_id'] != user_id:
        new_user_id = update_data['user_id']
        
        # Kiểm tra user_id mới chưa tồn tại
        existing_user_with_new_id = await db.get(User, new_user_id)
        if existing_user_with_new_id:
            raise HTTPException(status_code=400, detail=f"User ID '{new_user_id}' đã tồn tại")
        
        try:
            # Tạo user mới với ID mới
            new_user_data = {
                'user_id': new_user_id,
                'class_id': update_data.get('class_id', existing_user.class_id),
                'full_name': update_data.get('full_name', existing_user.full_name)
            }
            new_user = User(**new_user_data)
            db.add(new_user)
            
            # Update account table nếu có
            from app.models import Account
            account_result = await db.execute(select(Account).where(Account.user_id == user_id))
            account = account_result.scalars().first()
            if account:
                account.user_id = new_user_id
            
            # Xóa user cũ
            await db.delete(existing_user)
            
            await db.commit()
            await db.refresh(new_user)
            return new_user
            
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=f"Lỗi thay đổi user_id: {str(e)}")
    
    # Update thông tin bình thường (không đổi user_id)
    for field, value in update_data.items():
        setattr(existing_user, field, value)
    
    try:
        await db.commit()
        await db.refresh(existing_user)
        return existing_user
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi cập nhật: {str(e)}")

@router.delete("/{user_id}")
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Xóa người dùng khỏi hệ thống."""
    existing = await db.get(User, user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    await db.delete(existing)
    await db.commit()
    return {"message": f"Đã xóa người dùng {user_id}"}
