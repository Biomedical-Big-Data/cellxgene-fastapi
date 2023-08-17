import jwt
from random import Random
from hashlib import md5
from datetime import datetime, timedelta
from conf import config
from orm import crud
from orm.db_model import cellxgene
from sqlalchemy.orm import Session
from orm.schema.response import ResponseMessage


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
    expire_time: int = config.JWT_EXPIRE_TIME,
    secret_key: str = config.JWT_SECRET_KEY,
):
    token_dict = {
        "expire_time": (datetime.now() + timedelta(minutes=expire_time)).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "email_address": email_address,
    }
    jwt_token = jwt.encode(token_dict, secret_key, algorithm="HS256")
    return jwt_token


def check_token_for_verify_email(
    db: Session, token: str, secret_key: str = config.JWT_SECRET_KEY
):
    token_dict = jwt.decode(jwt=token, key=secret_key, algorithms="HS256")
    email_address = token_dict.get("email_address", "")
    expire_time = token_dict.get("expire_time", "")
    if not email_address or not expire_time:
        return ResponseMessage(status="0201", data="", message="token错误")
    if expire_time < datetime.now().strftime("%Y-%m-%d %H:%M:%S"):
        return ResponseMessage(status="0201", data="", message="token已过期")
    user_info = crud.get_user(
        db, filters=[cellxgene.User.email_address == email_address]
    ).first()
    if not user_info:
        return ResponseMessage(status="0201", data="", message="用户错误")
    return email_address


if __name__ == "__main__":
    pass
    # salt, md5_pwd = create_md5('123456')
    # print(salt, md5_pwd)
    # salt = create_salt(24)
    # print(salt)
    # jwt_token = create_token(email_address="test", user_password='12312', expire_time=30)
    # print(jwt_token)
