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
        from_attributes = True

class LoginRequest(BaseModel):
    """
    Lược đồ yêu cầu đăng nhập với ID người dùng và mật khẩu.
    """
    user_id: str
    password: str

class TokenResponse(BaseModel):
    """
    Lược đồ phản hồi token sau đăng nhập thành công.
    """
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str
