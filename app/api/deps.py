from fastapi import Header, HTTPException, status, Depends, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Optional
import time
import secrets
from app.core.config import settings

security = HTTPBasic()

def verify_admin_credentials(credentials: HTTPBasicCredentials) -> bool:
    """
    Xác thực thông tin quản trị với so sánh thời gian không đổi.
    """
    is_correct_user = secrets.compare_digest(credentials.username, settings.ADMIN_USERNAME)
    is_correct_pass = secrets.compare_digest(credentials.password, settings.SECRET_KEY)
    return is_correct_user and is_correct_pass

async def verify_admin_auth(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """
    Phụ thuộc cho xác thực HTTP Basic.
    """
    if not verify_admin_credentials(credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thông tin xác thực không chính xác",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

async def verify_device_or_admin(
    request: Request,
    x_timestamp: int = Header(..., alias="X-TIMESTAMP", description="Dấu thời gian Unix để chống tấn công replay"),
    x_api_key: Optional[str] = Header(None, alias="X-API-KEY", description="Khóa phần cứng (tự động bỏ qua nếu đã đăng nhập quản trị)")
) -> bool:
    """
    Middleware xác thực hỗn hợp với xác thực thời gian và truy cập ưu tiên.
    """
    
    # Xác thực dấu thời gian để ngăn chặn tấn công replay
    current_time = int(time.time())
    if abs(current_time - x_timestamp) > 30:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Yêu cầu bị từ chối do sai lệch thời gian (tấn công replay)"
        )

    # Ưu tiên: Kiểm tra xác thực quản trị qua header Authorization
    auth_header = request.headers.get("Authorization")
    if auth_header:
        try:
            scheme, param = auth_header.split()
            if scheme.lower() == "basic":
                import base64
                decoded = base64.b64decode(param).decode("utf-8")
                username, password = decoded.split(":")
                creds = HTTPBasicCredentials(username=username, password=password)
                if verify_admin_credentials(creds):
                    return True 
        except Exception:
            pass 

    # Dự phòng: Xác thực khóa API phần cứng
    if x_api_key == settings.HARDWARE_API_KEY:
        return True

    # Từ chối nếu không có xác thực nào vượt qua
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Yêu cầu cần có X-API-KEY hoặc đăng nhập quản trị",
    )