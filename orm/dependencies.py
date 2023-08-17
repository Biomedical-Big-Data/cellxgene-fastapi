import jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from starlette import status
from orm.database import SessionLocal
from conf import config
from datetime import datetime
from orm import crud
from orm.db_model import cellxgene


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
JWT_SECRET = config.JWT_SECRET_KEY


def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.rollback()
    finally:
        db.close()


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_dict = jwt.decode(jwt=token, key=JWT_SECRET, algorithms="HS256")
        email_address = token_dict.get("email_address", "")
        expire_time = token_dict.get("expire_time", "")
        if not email_address or not expire_time:
            raise credentials_exception
        if expire_time < datetime.now().strftime("%Y-%m-%d %H:%M:%S"):
            raise credentials_exception
        user_dict = crud.get_user(
            next(get_db()), [cellxgene.User.email_address == email_address]
        ).first()
        if not user_dict:
            raise credentials_exception
        return email_address
    except jwt.ExpiredSignatureError as e:
        print(e)
        raise credentials_exception
    except jwt.exceptions.PyJWTError as e:
        print(e)
        raise credentials_exception
