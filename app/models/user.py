"""
Module định nghĩa mô hình ORM cho thực thể User.

Quản lý thông tin cơ bản của người dùng trong hệ thống điểm danh.
"""

from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    """
    Mô hình ORM cho người dùng với ID, ID lớp và tên đầy đủ.
    
    Liên kết với các profile sinh viên/giảng viên và tài khoản.
    """
    __tablename__ = "users"

    # Khóa chính: ID người dùng duy nhất
    user_id = Column(String(32), primary_key=True, index=True)
    
    # Khóa ngoại: Liên kết với lớp học (có thể null)
    class_id = Column(String(20), ForeignKey("class.class_id"), nullable=True)
    
    # Tên đầy đủ của người dùng
    full_name = Column(Text, nullable=False)
    
    # Quan hệ sử dụng chuỗi để tránh import vòng
    account = relationship("Account", back_populates="user", uselist=False, cascade="all, delete-orphan")
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    lecturer_profile = relationship("LecturerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    fingerprints = relationship("Fingerprint", back_populates="user")