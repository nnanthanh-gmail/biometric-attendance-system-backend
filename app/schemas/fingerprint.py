from pydantic import BaseModel

class FingerprintBase(BaseModel):
    """
    Lược đồ cơ sở cho vân tay với ID và ID người dùng.
    """
    finger_id: str
    user_id: str
    # Không hiển thị finger_data trong API thông thường để bảo mật.

class FingerprintCreate(FingerprintBase):
    """
    Lược đồ tạo vân tay với dữ liệu.
    """
    finger_data: bytes

class FingerprintResponse(FingerprintBase):
    """
    Lược đồ phản hồi vân tay.
    """
    class Config:
        orm_mode = True
