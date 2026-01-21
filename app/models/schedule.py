from sqlalchemy import Column, Integer, String, Date, SmallInteger, Boolean, ForeignKey
from app.db.base import Base

class Schedule(Base):
    """
    Mô hình ORM cho lịch trình với ID, môn học, phòng, giảng viên, lớp, ngày, kỳ và trạng thái mở.
    """
    __tablename__ = "schedule"

    schedule_id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(String(20), ForeignKey("subject.subject_id"), nullable=False)
    room_id = Column(String(20), ForeignKey("room.room_id"), nullable=False)
    lecturer_id = Column(String(32), ForeignKey("users.user_id"), nullable=False)
    class_id = Column(String(20), ForeignKey("class.class_id"), nullable=False)
    learn_date = Column(Date, nullable=False)
    start_period = Column(SmallInteger, nullable=False)
    end_period = Column(SmallInteger, nullable=False)
    is_open = Column(Boolean, default=False)
