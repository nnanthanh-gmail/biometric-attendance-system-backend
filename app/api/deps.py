"""
Dependencies cho authentication và security.

Cung cấp JWT token handling, password hashing, admin auth và device verification.
"""

from fastapi import Header, HTTPException, status, Depends, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import time
import secrets
import base64
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

security = HTTPBasic()
bearer_security = HTTPBearer()

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def verify_admin_credentials(credentials: HTTPBasicCredentials) -> bool:
    """
    Xác thực credentials admin với constant-time comparison.

    Args:
        credentials: HTTP Basic credentials

    Returns:
        bool: True nếu credentials hợp lệ
    """
    is_correct_user = secrets.compare_digest(credentials.username, settings.ADMIN_USERNAME)
    is_correct_pass = secrets.compare_digest(credentials.password, settings.SECRET_KEY)
    return is_correct_user and is_correct_pass

async def verify_admin_auth(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """
    Dependency xác thực HTTP Basic cho admin users.

    Args:
        credentials: HTTP Basic credentials

    Returns:
        str: Admin username nếu authenticated

    Raises:
        HTTPException: Nếu authentication thất bại
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
    x_timestamp: int = Header(..., alias="X-TIMESTAMP", description="Unix timestamp chống replay attack"),
    x_api_key: Optional[str] = Header(None, alias="X-API-KEY", description="API key thiết bị phần cứng")
) -> bool:
    """
    Authentication hybrid cho device hoặc admin với validation timestamp.

    Args:
        request: FastAPI request object
        x_timestamp: Unix timestamp chống replay attack
        x_api_key: API key thiết bị phần cứng

    Returns:
        bool: True nếu authentication thành công

    Raises:
        HTTPException: Nếu authentication hoặc timestamp validation thất bại
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

def hash_password(password: str) -> str:
    """
    Hash password sử dụng bcrypt.

    Args:
        password: Plain text password

    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password với hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        bool: True nếu password khớp
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Tạo JWT access token.

    Args:
        data: Payload data để encode
        expires_delta: Optional expiration time

    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> dict:
    """
    Verify và decode JWT token.

    Args:
        token: JWT token string

    Returns:
        dict: Decoded payload

    Raises:
        HTTPException: Nếu token invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_security)) -> dict:
    """
    Dependency lấy thông tin user hiện tại từ JWT token.

    Args:
        credentials: Bearer token credentials

    Returns:
        dict: Thông tin user (user_id, role)

    Raises:
        HTTPException: Nếu token invalid hoặc thiếu user data
    """
    payload = verify_token(credentials.credentials)
    user_id: str = payload.get("sub")
    role: str = payload.get("role")
    if user_id is None or role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token thiếu thông tin user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"user_id": user_id, "role": role}