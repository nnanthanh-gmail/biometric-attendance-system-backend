from sqlalchemy import Column, String, Text
from app.db.base import Base

class Room(Base):
    """
    Mô hình ORM cho phòng với ID và tên.
    """
    __tablename__ = "room"

    room_id = Column(String(20), primary_key=True)
    room_name = Column(Text, nullable=False)
