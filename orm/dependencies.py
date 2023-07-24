from fastapi import Header, HTTPException
from orm.database import SessionLocal
from conf import config


def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.rollback()
    finally:
        db.close()
