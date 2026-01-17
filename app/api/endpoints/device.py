from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.db.session import get_db

router = APIRouter()

@router.post("/checkin")
async def device_checkin(
    # Dependency verify_device_or_admin sẽ xử lý logic.
    # Trên Docs chỉ cần nhập Timestamp, hệ thống tự nhận diện Session Admin.
    is_valid: bool = Depends(deps.verify_device_or_admin),
    
    db: AsyncSession = Depends(get_db)
):
    """
    API Check-in cho thiết bị.
    - Nếu test trên Docs: Chỉ cần nhập X-TIMESTAMP (vì đã login Admin).
    - Nếu device thật gọi: Gửi kèm X-API-KEY và X-TIMESTAMP trong Header.
    """
    return {"status": "success", "message": "Device authenticated successfully"}