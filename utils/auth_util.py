import jwt
from random import Random
from hashlib import md5
from datetime import datetime, timedelta
from conf import config
from orm import crud
from orm.db_model import cellxgene
from sqlalchemy.orm import Session
from orm.schema.exception_model import CREDENTIALS_EXCEPTION


def create_salt(length: int = 8):
    salt = ""
    chars = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789"
    len_chars = len(chars) - 1
    random = Random()
    for i in range(length):
        salt += chars[random.randint(0, len_chars)]
    return salt


def create_md5_password(salt: str | None, password: str):
    if not salt:
        salt = create_salt()
    md5_pwd = md5()
    md5_pwd.update((password + salt).encode("utf-8"))
    return salt, md5_pwd.hexdigest()


def create_token(
    email_address: str,
    expire_time: int = config.JWT_VERIFY_EXPIRE_TIME,
    secret_key: str = config.JWT_SECRET_KEY,
) -> str:
    token_dict = {
        "expire_time": (datetime.now() + timedelta(minutes=expire_time)).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "email_address": email_address,
    }
    jwt_token = jwt.encode(token_dict, secret_key, algorithm=config.JWT_ALGORITHMS)
    return jwt_token


def check_token_for_verify_email(
    db: Session, token: str, secret_key: str = config.JWT_SECRET_KEY
) -> str:
    try:
        token_dict = jwt.decode(
            jwt=token, key=secret_key, algorithms=config.JWT_ALGORITHMS
        )
        email_address = token_dict.get("email_address", "")
        expire_time = token_dict.get("expire_time", "")
        if not email_address or not expire_time:
            raise CREDENTIALS_EXCEPTION
        if expire_time < datetime.now().strftime("%Y-%m-%d %H:%M:%S"):
            raise CREDENTIALS_EXCEPTION
        user_info = crud.get_user(
            db, filters=[cellxgene.User.email_address == email_address]
        ).first()
        if not user_info:
            raise CREDENTIALS_EXCEPTION
        return email_address
    except jwt.ExpiredSignatureError as e:
        raise CREDENTIALS_EXCEPTION
    except jwt.exceptions.PyJWTError as e:
        raise CREDENTIALS_EXCEPTION


if __name__ == "__main__":
    pass
    # salt, md5_pwd = create_md5('123456')
    # print(salt, md5_pwd)
    # salt = create_salt(24)
    # print(salt)
    # jwt_token = create_token(email_address="test", user_password='12312', expire_time=30)
    # print(jwt_token)
