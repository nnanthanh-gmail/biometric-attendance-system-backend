from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api import deps
from app.db.session import get_db
from app.models.user import User

router = APIRouter()

@router.get("/")
async def read_users(
    # Dependency này sẽ kích hoạt Popup nếu chưa đăng nhập.
    # Khi đã đăng nhập, thông tin Basic Auth tự động gửi kèm header, không cần input tay.
    current_user: str = Depends(deps.verify_admin_auth),
    
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    """
    API lấy danh sách Users.
    Yêu cầu: Đăng nhập Basic Auth (User + Secret Key).
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()