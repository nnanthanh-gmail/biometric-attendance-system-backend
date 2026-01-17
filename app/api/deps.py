from fastapi import Header, HTTPException, status, Depends, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Optional
import time
import secrets
from app.core.config import settings

security = HTTPBasic()

def verify_admin_credentials(credentials: HTTPBasicCredentials) -> bool:
    """
    Kiểm tra thông tin đăng nhập Basic Auth.
    Quy tắc: 
    - Username: So khớp với ADMIN_USERNAME trong .env
    - Password: So khớp với SECRET_KEY trong .env
    """
    is_correct_user = secrets.compare_digest(credentials.username, settings.ADMIN_USERNAME)
    is_correct_pass = secrets.compare_digest(credentials.password, settings.SECRET_KEY)
    return is_correct_user and is_correct_pass

async def verify_admin_auth(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """
    Dependency bắt buộc cho các API cần quyền Admin.
    Nếu chưa đăng nhập, trả về 401 để trình duyệt hiện Popup.
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
    x_timestamp: int = Header(..., alias="X-TIMESTAMP", description="Unix Timestamp để chống Replay Attack"),
    x_api_key: Optional[str] = Header(None, alias="X-API-KEY", description="Key phần cứng (Tự động bỏ qua nếu đã login Admin)")
) -> bool:
    """
    Cơ chế xác thực hỗn hợp cho Device Endpoint:
    1. Kiểm tra Timestamp (Bắt buộc).
    2. Kiểm tra quyền truy cập:
       - Ưu tiên 1: Nếu Request có Header Basic Auth hợp lệ (đã login trên trình duyệt) -> CHO PHÉP.
       - Ưu tiên 2: Nếu có X-API-KEY khớp với HARDWARE_API_KEY -> CHO PHÉP.
    """
    
    # 1. Kiểm tra tính hợp lệ của thời gian (chống Replay Attack)
    current_time = int(time.time())
    if abs(current_time - x_timestamp) > 30:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Yêu cầu bị từ chối do sai lệch thời gian (Replay Attack)"
        )

    # 2. Kiểm tra xem người dùng có đang đăng nhập bằng Basic Auth (Admin) không
    # Lấy header Authorization từ request
    auth_header = request.headers.get("Authorization")
    if auth_header:
        try:
            # Tái sử dụng logic của HTTPBasic để parse header
            scheme, param = auth_header.split()
            if scheme.lower() == "basic":
                import base64
                decoded = base64.b64decode(param).decode("utf-8")
                username, password = decoded.split(":")
                # Tạo đối tượng credentials tạm để kiểm tra
                creds = HTTPBasicCredentials(username=username, password=password)
                if verify_admin_credentials(creds):
                    return True # Đã đăng nhập Admin -> Cho phép đi tiếp
        except Exception:
            pass # Nếu lỗi parse Basic Auth thì bỏ qua, chuyển sang check Hardware Key

    # 3. Nếu không phải Admin, kiểm tra Key phần cứng (Device thật)
    if x_api_key == settings.HARDWARE_API_KEY:
        return True

    # 4. Nếu cả hai đều sai
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Yêu cầu cần có X-API-KEY hoặc đăng nhập Admin",
    )