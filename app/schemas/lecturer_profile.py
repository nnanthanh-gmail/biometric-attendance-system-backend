from pydantic import BaseModel
from typing import Optional

class LecturerProfileBase(BaseModel):
    """
    Lược đồ cơ sở cho hồ sơ giảng viên với ID người dùng, khoa, bằng cấp và lĩnh vực nghiên cứu.
    """
    user_id: str
    faculty_id: str
    degree: str
    research_area: Optional[str] = None
    profile_image_url: Optional[str] = None

class LecturerProfileCreate(LecturerProfileBase):
    """
    Lược đồ tạo hồ sơ giảng viên.
    """
    pass

class LecturerProfileResponse(LecturerProfileBase):
    """
    Lược đồ phản hồi hồ sơ giảng viên.
    """
    class Config:
        from_attributes = True
