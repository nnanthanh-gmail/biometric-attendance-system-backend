from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Chuỗi kết nối cơ sở dữ liệu
    DATABASE_URL: str
    
    # Khóa bí mật dùng làm mật khẩu đăng nhập cho Admin
    SECRET_KEY: str
    
    # Khóa xác thực dành riêng cho thiết bị phần cứng (Raspberry Pi)
    HARDWARE_API_KEY: str
    
    # Tên tài khoản đăng nhập Admin
    ADMIN_USERNAME: str = "admin"

    class Config:
        env_file = ".env"
        # Bỏ qua các biến thừa trong file .env để tránh lỗi validation
        extra = "ignore" 

settings = Settings()