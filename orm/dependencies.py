from fastapi import Header, HTTPException
from orm.database import SessionLocal
from conf import config


async def verify_token(x_token: str = Header()):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def get_query_token(token: str):
    if token != "jessica":
        raise HTTPException(status_code=400, detail="No Jessica token provided")


def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.rollback()
    finally:
        db.close()
