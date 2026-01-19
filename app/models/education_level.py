from sqlalchemy import Column, String, Text
from app.db.base import Base

class EducationLevel(Base):
    """
    Mô hình ORM cho cấp độ giáo dục với ID và tên.
    """
    __tablename__ = "education_level"

    edu_level_id = Column(String(20), primary_key=True)
    edu_level_name = Column(Text, nullable=False)
