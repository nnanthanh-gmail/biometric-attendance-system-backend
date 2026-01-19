from pydantic import BaseModel
from datetime import datetime

class AttendanceBase(BaseModel):
    """
    Lược đồ cơ sở cho điểm danh với lịch trình, người dùng, trạng thái và thời gian.
    """
    schedule_id: int
    user_id: str
    status: bool
    attend_time: datetime

class AttendanceCreate(AttendanceBase):
    """
    Lược đồ tạo điểm danh.
    """
    pass

class AttendanceResponse(AttendanceBase):
    """
    Lược đồ phản hồi điểm danh với ID.
    """
    attend_id: int
    
    class Config:
        orm_mode = True
