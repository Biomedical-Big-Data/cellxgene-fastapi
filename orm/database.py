from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

USER_DATABASE_URL = "mysql+pymysql://root:admin1234@192.168.6.225:3306/?charset=utf8"

user_engine = create_engine(USER_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=user_engine)

Base = declarative_base()
