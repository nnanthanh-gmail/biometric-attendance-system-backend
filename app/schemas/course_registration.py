from pydantic import BaseModel
from datetime import datetime

class CourseRegBase(BaseModel):
    """
    Lược đồ cơ sở cho đăng ký khóa học với người dùng, môn học, lớp, học kỳ và năm.
    """
    user_id: str
    subject_id: str
    host_class_id: str
    semester: int
    year: int

class CourseRegCreate(CourseRegBase):
    """
    Lược đồ tạo đăng ký khóa học.
    """
    pass

class CourseRegResponse(CourseRegBase):
    """
    Lược đồ phản hồi đăng ký khóa học với ID và dấu thời gian.
    """
    reg_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True
