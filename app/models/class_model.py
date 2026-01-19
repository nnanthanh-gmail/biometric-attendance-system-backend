from sqlalchemy import Column, String, Text, SmallInteger, ForeignKey
from app.db.base import Base

class ClassModel(Base):
    """
    Mô hình ORM cho lớp với ID, chuyên ngành, cấp độ, tên, khóa học và năm.
    """
    __tablename__ = "class"

    class_id = Column(String(20), primary_key=True)
    major_id = Column(String(20), ForeignKey("major.major_id"), nullable=False)
    edu_level_id = Column(String(20), ForeignKey("education_level.edu_level_id"), nullable=False)
    class_name = Column(Text, nullable=False)
    course = Column(String(10), nullable=False)  # Khóa học như K19, K20
    enroll_year = Column(SmallInteger, nullable=False)
