from pydantic import BaseModel
from datetime import date
from typing import Optional

class ScheduleBase(BaseModel):
    """
    Lược đồ cơ sở cho lịch trình với môn học, phòng, giảng viên, lớp, ngày, kỳ và trạng thái mở.
    """
    subject_id: str
    room_id: str
    lecturer_id: str
    class_id: str
    learn_date: date
    start_period: int
    end_period: int
    is_open: Optional[bool] = True

class ScheduleCreate(ScheduleBase):
    """
    Lược đồ tạo lịch trình.
    """
    pass

class ScheduleResponse(ScheduleBase):
    """
    Lược đồ phản hồi lịch trình với ID.
    """
    schedule_id: int  # ID tự tăng chỉ trong phản hồi
    
    class Config:
        orm_mode = True
