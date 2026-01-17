from pydantic import BaseModel
from datetime import date

class AttendanceCheckIn(BaseModel):
    fingerprint_id: str
    device_id: str
    # Timestamp sẽ được lấy từ Header để validate bảo mật

class AttendanceResponse(BaseModel):
    user_id: str
    full_name: str
    status: str
    time: str
