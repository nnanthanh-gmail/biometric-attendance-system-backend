# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.router import api_router  # Import Router tổng hợp từ router.py

def get_application() -> FastAPI:
    """
    Nhà máy cho ứng dụng FastAPI với CORS, bộ định tuyến và cài đặt.
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        debug=settings.DEBUG, # Hiển thị lỗi chi tiết nếu đang debug
    )

    # Cấu hình CORS (Cho phép Frontend React/Flutter gọi vào)
    if settings.BACKEND_CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Kết nối toàn bộ API Router vào App
    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application

app = get_application()

# Root endpoint để test server sống hay chết
@app.get("/")
def root():
    """
    Endpoint kiểm tra sức khỏe cho trạng thái hệ thống và liên kết tài liệu.
    """
    return {
        "message": "Biometric Attendance System API is running",
        "status": "ok",
        "docs_url": "/docs"
    }