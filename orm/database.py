from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from conf import config

USER_DATABASE_URL = config.DATABASE_URL

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
