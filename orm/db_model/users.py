from sqlalchemy import Column, DateTime, Integer, String, text
from sqlalchemy.dialects.mysql import TINYINT, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from dataclasses import dataclass

Base = declarative_base()
metadata = Base.metadata


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "users"}

    id = Column(Integer, primary_key=True)
    user_name = Column(String(255), nullable=False, unique=True)
    email_address = Column(VARCHAR(255), nullable=False, unique=True)
    organization = Column(String(255), nullable=False)
    salt = Column(String(255), nullable=False)
    user_password = Column(String(255), nullable=False)
    verify_state = Column(TINYINT(1), nullable=False)
    create_at = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    update_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )

    def to_dict(self):
        return {
            "user_name": self.user_name,
            "email_address": self.email_address,
            "organization": self.organization,
            "verify_state": self.verify_state,
            "create_at": self.create_at,
            "update_at": self.update_at,
        }
