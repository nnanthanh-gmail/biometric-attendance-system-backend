from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(String(50), primary_key=True, index=True)
    faculty_id = Column(String(50), ForeignKey("faculty.faculty_id"))
    class_id = Column(String(50), ForeignKey("class.class_id"))
    full_name = Column(String(100), nullable=False)

    # Quan hệ ngược (Optional)
    account = relationship("Account", back_populates="user", uselist=False)

class Account(Base):
    __tablename__ = "account"

    username = Column(String(50), primary_key=True)
    password = Column(String(255), nullable=False)
    role = Column(Integer, nullable=False) # 0: Sv, 1: GV, 2: Admin
    user_id = Column(String(50), ForeignKey("users.user_id"), unique=True)

    user = relationship("User", back_populates="account")
