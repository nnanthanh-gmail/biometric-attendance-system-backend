"""
Cấu hình bộ định tuyến API với nhóm điểm cuối.
"""
from fastapi import APIRouter

# Import chỉ các mô-đun điểm cuối hiện có
from app.api.endpoints import (
    users,
    account,
    student_profile,
    lecturer_profile,
    faculty,
    class_room,  # tệp hiện có là class_room.py
    subject,
    room,
    schedule,
    attendance,
    device
)

# Khởi tạo Router tổng
api_router = APIRouter()

# =================================================================
# 1. HỆ THỐNG LÕI & ĐỊNH DANH
# =================================================================

# Quản lý Users (CRUD cơ bản)
api_router.include_router(
    users.router, 
    prefix="/users", 
    tags=["Users"]
)

# Quản lý tài khoản & đăng nhập (Account)
api_router.include_router(
    account.router, 
    prefix="/accounts", 
    tags=["Accounts"]
)

# Quản lý thiết bị phần cứng (Hardware IoT)
api_router.include_router(
    device.router, 
    prefix="/device", 
    tags=["Hardware"]
)

# =================================================================
# 2. HỒ SƠ CÁ NHÂN
# =================================================================

# Hồ sơ sinh viên
api_router.include_router(
    student_profile.router, 
    prefix="/profiles/student", 
    tags=["Student Profiles"]
)

# Hồ sơ giảng viên
api_router.include_router(
    lecturer_profile.router, 
    prefix="/profiles/lecturer", 
    tags=["Lecturer Profiles"]
)

# =================================================================
# 3. CẤU TRÚC ĐÀO TẠO
# =================================================================

# Khoa (Faculty)
api_router.include_router(
    faculty.router, 
    prefix="/faculties", 
    tags=["Faculties"]
)

# Lớp hành chính (Class)
api_router.include_router(
    class_room.router, 
    prefix="/classes", 
    tags=["Classes"]
)

# =================================================================
# 4. KHÓA HỌC & CƠ SỞ VẬT CHẤT
# =================================================================

# Môn học (Subject)
api_router.include_router(
    subject.router, 
    prefix="/subjects", 
    tags=["Subjects"]
)

# Phòng học (Room)
api_router.include_router(
    room.router, 
    prefix="/rooms", 
    tags=["Rooms"]
)

# =================================================================
# 5. VẬN HÀNH HÀNG NGÀY
# =================================================================

# Thời khóa biểu (Schedule)
api_router.include_router(
    schedule.router, 
    prefix="/schedules", 
    tags=["Schedules"]
)

# Điểm danh (Attendance)
api_router.include_router(
    attendance.router, 
    prefix="/attendance", 
    tags=["Attendance Logs"]
)
