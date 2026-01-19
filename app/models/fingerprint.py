from sqlalchemy import Column, String, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from app.db.base import Base

class Fingerprint(Base):
    """
    Mô hình ORM cho vân tay với ID, ID người dùng và dữ liệu.
    """
    __tablename__ = "fingerprint"

    finger_id = Column(String(32), primary_key=True)
    user_id = Column(String(32), ForeignKey("users.user_id"), nullable=False)
    finger_data = Column(LargeBinary, nullable=False)  # Ánh xạ tới bytea PostgreSQL

    user = relationship("User", back_populates="fingerprints")
