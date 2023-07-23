from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "users"}

    id = Column(Integer, primary_key=True)
    user_name = Column(String(255), nullable=False, unique=True)
    user_password = Column(String(255), nullable=False)
    email_address = Column(String(255), nullable=False)
