"""
Module khởi tạo ứng dụng chính FastAPI.

Thiết lập ứng dụng với middleware CORS, định tuyến API và phục vụ file tĩnh.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api.router import api_router

def get_application() -> FastAPI:
    """
    Factory function tạo instance FastAPI với cấu hình đầy đủ.

    Thiết lập CORS cho frontend, tích hợp router API và mount thư mục uploads.

    Returns:
        FastAPI: Instance ứng dụng đã cấu hình
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        debug=settings.DEBUG,
    )

    # Middleware CORS cho cross-origin requests từ frontend
    if settings.BACKEND_CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Đăng ký tất cả API endpoints
    application.include_router(api_router, prefix=settings.API_V1_STR)

    # Phục vụ file tĩnh cho uploads
    application.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

    return application

# Instance ứng dụng singleton
app = get_application()

@app.get("/")
def health_check():
    """
    Endpoint health check cho monitoring hệ thống.

    Returns:
        dict: Thông tin trạng thái và link documentation
    """
    return {
        "message": "Biometric Attendance System API đang chạy",
        "status": "ok",
        "docs_url": "/docs"
    }