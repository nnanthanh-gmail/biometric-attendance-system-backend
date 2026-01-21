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

# Update: Dùng khi cập nhật (Input) - user_id là optional
class UserUpdate(BaseModel):
    """
    Lược đồ cập nhật người dùng.
    """
    user_id: Optional[str] = None
    class_id: Optional[str] = None
    full_name: Optional[str] = None

# Response: Dùng khi trả về Client (Output)
class UserResponse(UserBase):
    """
    Lược đồ phản hồi người dùng.
    """
    class Config:
        from_attributes = True  # Cho phép đọc dữ liệu từ đối tượng SQLAlchemy
