from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.db.session import get_db

# Khởi tạo Router cho phân vùng tài nguyên thiết bị
router = APIRouter()

@router.post("/checkin")
async def device_checkin(
    # Thực thi Middleware xác thực hỗn hợp (Hybrid Auth): Chấp nhận Admin Session hoặc Hardware Key
    is_valid: bool = Depends(deps.verify_device_or_admin),
    
    # Inject Database Session cho các thao tác dữ liệu không đồng bộ
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint cho check-in thiết bị phần cứng với xác thực hỗn hợp.
    """
    return {"status": "success", "message": "Device authenticated successfully"}