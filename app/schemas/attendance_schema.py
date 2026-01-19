from pydantic import BaseModel
from datetime import date

class AttendanceCheckIn(BaseModel):
    """
    DTO cho check-in thiết bị với ID sinh trắc học và khóa thiết bị.
    """
    fingerprint_id: str
    device_id: str
    # Dấu thời gian từ header để ngăn chặn tấn công replay.

class AttendanceResponse(BaseModel):
    """
    DTO cho phản hồi check-in với chi tiết người dùng và trạng thái.
    """
    user_id: str
    full_name: str
    status: str
    time: str