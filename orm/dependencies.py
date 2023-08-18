import jwt
import logging
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from orm.database import SessionLocal
from conf import config
from datetime import datetime
from orm import crud
from orm.db_model import cellxgene
from orm.schema.exception_model import CREDENTIALS_EXCEPTION, USERBLOCK_EXCEPTION


OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="/user/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.rollback()
    finally:
        db.close()


async def get_current_user(token: str = Depends(OAUTH2_SCHEME)):
    try:
        token_dict = jwt.decode(jwt=token, key=config.JWT_SECRET_KEY, algorithms="HS256")
        email_address = token_dict.get("email_address", "")
        expire_time = token_dict.get("expire_time", "")
        if not email_address or not expire_time:
            raise CREDENTIALS_EXCEPTION
        if expire_time < datetime.now().strftime("%Y-%m-%d %H:%M:%S"):
            raise CREDENTIALS_EXCEPTION
        user_info_model = crud.get_user(
            next(get_db()), [cellxgene.User.email_address == email_address]
        ).first()
        if not user_info_model:
            raise CREDENTIALS_EXCEPTION
        if user_info_model.state != config.UserStateConfig.USER_STATE_VERIFY:
            raise USERBLOCK_EXCEPTION
        return email_address
    except jwt.ExpiredSignatureError as e:
        logging.error('[ExpiredSignatureError]: {}'.format(str(e)))
        raise CREDENTIALS_EXCEPTION
    except jwt.exceptions.PyJWTError as e:
        logging.error('[PyJWTError]: {}'.format(str(e)))
        raise CREDENTIALS_EXCEPTION
