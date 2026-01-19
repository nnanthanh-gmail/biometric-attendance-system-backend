from sqlalchemy import Column, Integer, String, SmallInteger, TIMESTAMP, ForeignKey
from app.db.base import Base

class CourseRegistration(Base):
    """
    Mô hình ORM cho đăng ký khóa học với ID, người dùng, môn học, lớp, học kỳ, năm và dấu thời gian.
    """
    __tablename__ = "course_registration"

    reg_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(32), ForeignKey("users.user_id"), nullable=False)
    subject_id = Column(String(20), ForeignKey("subject.subject_id"), nullable=False)
    host_class_id = Column(String(20), ForeignKey("class.class_id"), nullable=False)
    semester = Column(SmallInteger, nullable=False)
    year = Column(SmallInteger, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
