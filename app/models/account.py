from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Account(Base):
    """
    Mô hình ORM cho tài khoản với ID người dùng, băm mật khẩu và vai trò.
    """
    __tablename__ = "account"

    user_id = Column(String(32), ForeignKey("users.user_id"), primary_key=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(1), nullable=False)

    user = relationship("User", back_populates="account")
