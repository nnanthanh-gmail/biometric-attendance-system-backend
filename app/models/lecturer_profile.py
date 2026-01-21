from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class LecturerProfile(Base):
    """
    Mô hình ORM cho hồ sơ giảng viên với ID người dùng, khoa, bằng cấp và lĩnh vực nghiên cứu.
    """
    __tablename__ = "lecturer_profile"

    user_id = Column(String(32), ForeignKey("users.user_id"), primary_key=True)
    faculty_id = Column(String(20), ForeignKey("faculty.faculty_id"), nullable=False)
    degree = Column(Text, nullable=False)
    research_area = Column(Text, nullable=True)
    profile_image_url = Column(Text, nullable=True)

    user = relationship("User", back_populates="lecturer_profile")
