"""
Module cấu hình ứng dụng tập trung.

Quản lý cấu hình type-safe sử dụng Pydantic, load từ file .env.
"""

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """
    Class cấu hình ứng dụng với validation type.

    Attributes:
        DATABASE_URL: Chuỗi kết nối PostgreSQL async
        SECRET_KEY: Key ký JWT cho authentication
        HARDWARE_API_KEY: API key xác thực thiết bị phần cứng
        ADMIN_USERNAME: Username admin mặc định
        PROJECT_NAME: Tên ứng dụng
        API_V1_STR: Prefix API version
        DEBUG: Cờ debug mode
        BACKEND_CORS_ORIGINS: Danh sách origins cho CORS
    """
    # Cấu hình database
    DATABASE_URL: str

    # Keys bảo mật
    SECRET_KEY: str
    HARDWARE_API_KEY: str

    # Credentials admin mặc định
    ADMIN_USERNAME: str = "admin"

    # Cấu hình ứng dụng
    PROJECT_NAME: str = "Biometric Attendance System"
    API_V1_STR: str = "/api"
    DEBUG: bool = False
    BACKEND_CORS_ORIGINS: List[str] = []

    class Config:
        """
        Cấu hình Pydantic cho loading environment.
        """
        env_file = ".env"
        extra = "ignore"

# Instance singleton cho toàn ứng dụng
settings = Settings()