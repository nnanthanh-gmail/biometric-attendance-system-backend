from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Sử dụng nhà cung cấp DB bất đồng bộ (đã nhập sai app.api.session)
from app.db.session import get_db
from app.api import deps

from app.models import LecturerProfile, Account
from app.schemas import LecturerProfileCreate, LecturerProfileResponse

router = APIRouter()

@router.get("/", response_model=List[LecturerProfileResponse])
async def read_lecturer_profiles(
    skip: int = 0,
    limit: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    API endpoint lấy danh sách hồ sơ giảng viên với phân trang offset/limit.

    Hỗ trợ phân trang bằng offset/limit để tối ưu hiệu suất.

    Args:
        skip: Số bản ghi bỏ qua (offset)
        limit: Số lượng bản ghi tối đa trả về
        db: Session database async

    Returns:
        List[LecturerProfileResponse]: Danh sách hồ sơ giảng viên
    """
    query = select(LecturerProfile).order_by(LecturerProfile.user_id.asc()).offset(skip)
    if limit is not None:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=LecturerProfileResponse)
async def create_lecturer_profile(
    profile: LecturerProfileCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(deps.verify_admin_auth)
):
    """Tạo hồ sơ giảng viên mới."""
    # Kiểm tra role
    account_result = await db.execute(select(Account).where(Account.user_id == profile.user_id))
    account = account_result.scalars().first()
    if not account or account.role != 'lecturer':
        raise HTTPException(status_code=400, detail="Chỉ có thể tạo hồ sơ giảng viên cho tài khoản có role 'lecturer'")
    
    existing = await db.get(LecturerProfile, profile.user_id)
    if existing:
        raise HTTPException(status_code=400, detail="Hồ sơ đã tồn tại cho ID người dùng này")
    new_profile = LecturerProfile(**profile.dict())
    db.add(new_profile)
    try:
        await db.commit()
        await db.refresh(new_profile)
        return new_profile
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Lỗi cơ sở dữ liệu")

@router.get("/{user_id}", response_model=LecturerProfileResponse)
async def read_lecturer_profile_by_id(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Lấy hồ sơ giảng viên theo ID người dùng."""
    profile = await db.get(LecturerProfile, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ giảng viên")
    return profile

@router.put("/{user_id}", response_model=LecturerProfileResponse)
async def update_lecturer_profile(
    user_id: str,
    profile_update: LecturerProfileCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(deps.verify_admin_auth)
):
    """Cập nhật hồ sơ giảng viên theo ID người dùng."""
    db_profile = await db.get(LecturerProfile, user_id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ giảng viên")

    for k, v in profile_update.dict(exclude_unset=True).items():
        setattr(db_profile, k, v)

    db.add(db_profile)
    await db.commit()
    await db.refresh(db_profile)
    return db_profile

@router.delete("/{user_id}")
async def delete_lecturer_profile(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(deps.verify_admin_auth)
):
    """Xóa hồ sơ giảng viên theo ID người dùng."""
    db_profile = await db.get(LecturerProfile, user_id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ giảng viên")
    
    await db.delete(db_profile)
    await db.commit()
    return {"message": f"Đã xóa hồ sơ giảng viên {user_id}"}
