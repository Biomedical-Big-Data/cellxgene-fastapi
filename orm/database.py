from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus as urlquote
from conf.config import MYSQL_USER, MYSQL_HOST, MYSQL_PORT, MYSQL_PASSWORD


USER_DATABASE_URL = f"mysql+pymysql://{urlquote(MYSQL_USER)}:{urlquote(MYSQL_PASSWORD)}@{urlquote(MYSQL_HOST)}:{urlquote(MYSQL_PORT)}/cellxgene?charset=utf8"

cellxgene_engine = create_engine(
    USER_DATABASE_URL,
    pool_size=20,
    max_overflow=20,
    pool_recycle=1800,
    echo=False,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cellxgene_engine)

Base = declarative_base()
