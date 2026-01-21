from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey
from app.db.base import Base

class Attendance(Base):
    """
    Mô hình ORM cho điểm danh với ID, lịch trình, người dùng, thời gian và trạng thái.
    """
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_id = Column(Integer, ForeignKey("schedule.schedule_id"), nullable=False)
    user_id = Column(String(32), ForeignKey("users.user_id"), nullable=False)
    time = Column(TIMESTAMP, nullable=False)
    status = Column(Boolean, nullable=False)
