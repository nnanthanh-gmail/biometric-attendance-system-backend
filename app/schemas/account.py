from pydantic import BaseModel

class AccountBase(BaseModel):
    """
    Lược đồ cơ sở cho tài khoản với ID người dùng và vai trò.
    """
    user_id: str
    role: str

class AccountCreate(AccountBase):
    """
    Lược đồ tạo tài khoản với mật khẩu.
    """
    password: str  # Mật khẩu chỉ cho tạo/đăng nhập

class AccountResponse(AccountBase):
    """
    Lược đồ phản hồi tài khoản.
    """
    class Config:
        orm_mode = True
