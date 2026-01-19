from sqlalchemy import Column, String, Text, ForeignKey
from app.db.base import Base

class Major(Base):
    """
    Mô hình ORM cho chuyên ngành với ID, khoa và tên.
    """
    __tablename__ = "major"

    major_id = Column(String(20), primary_key=True)
    faculty_id = Column(String(20), ForeignKey("faculty.faculty_id"), nullable=False)
    major_name = Column(Text, nullable=False)
