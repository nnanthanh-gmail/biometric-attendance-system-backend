from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.api import deps
from app.db.session import get_db
from app.models import StudentProfile, Account
from app.schemas import StudentProfileBase

router = APIRouter()

@router.get("/", response_model=List[StudentProfileBase])
async def read_student_profiles(
    skip: int = 0,
    limit: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    API endpoint lấy danh sách hồ sơ sinh viên với phân trang offset/limit.

    Hỗ trợ phân trang bằng offset/limit để tối ưu hiệu suất.

    Args:
        skip: Số bản ghi bỏ qua (offset)
        limit: Số lượng bản ghi tối đa trả về
        db: Session database async

    Returns:
        List[StudentProfileBase]: Danh sách hồ sơ sinh viên
    """
    query = select(StudentProfile).order_by(StudentProfile.user_id.asc()).offset(skip)
    if limit is not None:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{user_id}", response_model=StudentProfileBase)
async def get_profile(user_id: str, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Lấy hồ sơ sinh viên theo ID người dùng."""
    res = await db.get(StudentProfile, user_id)
    if not res: raise HTTPException(404, "Not Found")
    return res

@router.post("/")
async def create_profile(data: StudentProfileBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Tạo hồ sơ sinh viên mới."""
    # Kiểm tra role của user_id
    account_result = await db.execute(select(Account).where(Account.user_id == data.user_id))
    account = account_result.scalars().first()
    if not account or account.role != 'student':
        raise HTTPException(status_code=400, detail="Chỉ có thể tạo hồ sơ sinh viên cho tài khoản có role 'student'")
    
    obj = StudentProfile(**data.dict())
    db.add(obj)
    await db.commit()
    return obj

@router.put("/{user_id}", response_model=StudentProfileBase)
async def update_profile(user_id: str, data: StudentProfileBase, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Cập nhật hồ sơ sinh viên."""
    existing = await db.get(StudentProfile, user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Hồ sơ sinh viên không tồn tại")
    
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

@router.delete("/{user_id}")
async def delete_profile(user_id: str, db: AsyncSession = Depends(get_db), _: str = Depends(deps.verify_admin_auth)):
    """Xóa hồ sơ sinh viên."""
    existing = await db.get(StudentProfile, user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Hồ sơ sinh viên không tồn tại")
    await db.delete(existing)
    await db.commit()
    return {"message": f"Đã xóa hồ sơ sinh viên {user_id}"}
