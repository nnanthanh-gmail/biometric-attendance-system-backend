from pydantic import BaseModel
from datetime import date

class StudentProfileBase(BaseModel):
    """
    Lược đồ cơ sở cho hồ sơ sinh viên với ID người dùng, ngày sinh, giới tính, điện thoại và địa chỉ.
    """
    user_id: str
    birth_date: date
    is_female: bool = False
    phone: str
    address: str
    profile_image_url: str | None = None

class StudentProfileCreate(StudentProfileBase):
    """
    Lược đồ tạo hồ sơ sinh viên.
    """
    pass

class StudentProfileResponse(StudentProfileBase):
    """
    Lược đồ phản hồi hồ sơ sinh viên.
    """
    class Config:
        from_attributes = True
