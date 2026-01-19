from pydantic import BaseModel
from typing import Optional

# Base: Các trường chung
class UserBase(BaseModel):
    """
    Lược đồ cơ sở cho người dùng với ID, ID lớp tùy chọn và tên đầy đủ.
    """
    user_id: str
    class_id: Optional[str] = None
    full_name: str

# Create: Dùng khi tạo mới (Input)
class UserCreate(UserBase):
    """
    Lược đồ tạo người dùng.
    """
    pass

# Response: Dùng khi trả về Client (Output)
class UserResponse(UserBase):
    """
    Lược đồ phản hồi người dùng.
    """
    class Config:
        orm_mode = True  # Cho phép đọc dữ liệu từ đối tượng SQLAlchemy
