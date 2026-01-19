from sqlalchemy import Column, String, Boolean, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class StudentProfile(Base):
    """
    Mô hình ORM cho hồ sơ sinh viên với ID người dùng, ngày sinh, giới tính, điện thoại và địa chỉ.
    """
    __tablename__ = "student_profile"

    user_id = Column(String(32), ForeignKey("users.user_id"), primary_key=True)
    birth_date = Column(Date, nullable=False)
    gender = Column(Boolean, nullable=False)
    phone = Column(String(15), nullable=False)
    address = Column(Text, nullable=False)

    user = relationship("User", back_populates="student_profile")
