from sqlalchemy import Column, String, Text
from app.db.base import Base

class Faculty(Base):
    """
    Mô hình ORM cho khoa với ID và tên.
    """
    __tablename__ = "faculty"

    faculty_id = Column(String(20), primary_key=True)
    faculty_name = Column(Text, nullable=False)
