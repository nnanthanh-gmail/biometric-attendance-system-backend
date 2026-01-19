from sqlalchemy import Column, String, Text, SmallInteger
from app.db.base import Base

class Subject(Base):
    """
    Mô hình ORM cho môn học với ID, tên, tín chỉ, lý thuyết, thực hành và học kỳ.
    """
    __tablename__ = "subject"

    subject_id = Column(String(20), primary_key=True)
    subject_name = Column(Text, nullable=False)
    credits = Column(SmallInteger, nullable=False)
    theory = Column(SmallInteger, nullable=False)
    practice = Column(SmallInteger, nullable=False)
    semester = Column(SmallInteger, nullable=False)
