from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    """
    Mô hình ORM cho người dùng với ID, ID lớp và tên đầy đủ.
    """
    __tablename__ = "users"

    user_id = Column(String(32), primary_key=True, index=True)
    class_id = Column(String(20), ForeignKey("class.class_id"), nullable=True)
    full_name = Column(Text, nullable=False)
    
    # Quan hệ sử dụng chuỗi để tránh import vòng
    account = relationship("Account", back_populates="user", uselist=False, cascade="all, delete-orphan")
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    lecturer_profile = relationship("LecturerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    fingerprints = relationship("Fingerprint", back_populates="user")