"""
Module cấu hình router API tổng hợp.

Tổ chức và tích hợp tất cả endpoint routers theo nhóm chức năng để dễ bảo trì.
"""

from fastapi import APIRouter

# Import tất cả endpoint modules
from app.api.endpoints import (
    users,
    account,
    student_profile,
    lecturer_profile,
    faculty,
    major,
    education_level,
    class_room,
    subject,
    room,
    schedule,
    course_registration,
    attendance,
    fingerprint,
    device,
    dashboard,
    upload
)

# Khởi tạo router chính
api_router = APIRouter()

# =================================================================
# HỆ THỐNG LÕI & XÁC THỰC
# =================================================================

# Quản lý users cơ bản
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

# Quản lý tài khoản và xác thực
api_router.include_router(
    account.router,
    prefix="/accounts",
    tags=["Accounts"]
)

# Quản lý thiết bị phần cứng IoT
api_router.include_router(
    device.router,
    prefix="/device",
    tags=["Hardware"]
)

# =================================================================
# HỒ SƠ NGƯỜI DÙNG
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

# Dữ liệu vân tay sinh trắc
api_router.include_router(
    fingerprint.router,
    prefix="/fingerprints",
    tags=["Fingerprints"]
)

# =================================================================
# CẤU TRÚC ĐÀO TẠO
# =================================================================

# Quản lý khoa
api_router.include_router(
    faculty.router,
    prefix="/faculties",
    tags=["Faculties"]
)

# Quản lý chuyên ngành
api_router.include_router(
    major.router,
    prefix="/majors",
    tags=["Majors"]
)

# Quản lý cấp độ giáo dục
api_router.include_router(
    education_level.router,
    prefix="/education_levels",
    tags=["Education Levels"]
)

# Quản lý lớp học
api_router.include_router(
    class_room.router,
    prefix="/classes",
    tags=["Classes"]
)

# =================================================================
# KHÓA HỌC & CƠ SỞ VẬT CHẤT
# =================================================================

# Quản lý môn học
api_router.include_router(
    subject.router,
    prefix="/subjects",
    tags=["Subjects"]
)

# Quản lý phòng học
api_router.include_router(
    room.router,
    prefix="/rooms",
    tags=["Rooms"]
)

# =================================================================
# HOẠT ĐỘNG HẰNG NGÀY
# =================================================================

# Quản lý thời khóa biểu
api_router.include_router(
    schedule.router,
    prefix="/schedules",
    tags=["Schedules"]
)

# Nhật ký điểm danh
api_router.include_router(
    attendance.router,
    prefix="/attendance",
    tags=["Attendance Logs"]
)

# Đăng ký khóa học
api_router.include_router(
    course_registration.router,
    prefix="/course_registrations",
    tags=["Course Registrations"]
)

# Dashboard và phân tích
api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard & Analytics"]
)

# Upload files
api_router.include_router(
    upload.router,
    prefix="/upload",
    tags=["File Upload"]
)
