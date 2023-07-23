from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from conf import config

USER_DATABASE_URL = config.TEST_USER_DATABASE_URL

user_engine = create_engine(USER_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=user_engine)

Base = declarative_base()
