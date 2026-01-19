from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # URL kết nối PostgreSQL
    DATABASE_URL: str
    
    # Khóa ký cho xác thực quản trị
    SECRET_KEY: str
    
    # Khóa API cho xác thực phần cứng
    HARDWARE_API_KEY: str
    
    # Tên người dùng quản trị mặc định
    ADMIN_USERNAME: str = "admin"

    # Cài đặt ứng dụng
    PROJECT_NAME: str = "Biometric Attendance System"
    API_V1_STR: str = "/api"  # thay đổi từ "/api/v1" thành "/api"
    DEBUG: bool = False
    BACKEND_CORS_ORIGINS: List[str] = []

    class Config:
        # Tải từ tệp .env
        env_file = ".env"
        # Bỏ qua biến env bị thiếu
        extra = "ignore" 

# Khởi tạo phiên bản singleton cho toàn bộ ứng dụng
settings = Settings()