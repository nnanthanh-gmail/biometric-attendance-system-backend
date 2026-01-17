from fastapi import APIRouter
# THAY ĐỔI 1: Thêm users vào dòng import
from app.api.endpoints import device, users

api_router = APIRouter()

# Gom nhóm các endpoint
api_router.include_router(device.router, prefix="/device", tags=["Hardware"])

# THAY ĐỔI 2: Bỏ dấu # ở đầu dòng dưới đây
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# Auth vẫn tạm thời đóng nếu chưa viết code cho auth.py
# api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
