from pydantic import BaseModel
from datetime import datetime

class AttendanceBase(BaseModel):
    """
    Lược đồ cơ sở cho điểm danh với lịch trình, người dùng, trạng thái và thời gian.
    """
    schedule_id: int
    user_id: str
    status: bool
    time: datetime

class AttendanceCreate(AttendanceBase):
    """
    Lược đồ tạo điểm danh.
    """
    pass

class AttendanceResponse(AttendanceBase):
    """
    Lược đồ phản hồi điểm danh với ID.
    """
    id: int
    
    class Config:
        from_attributes = True
