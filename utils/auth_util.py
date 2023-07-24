import jwt
from random import Random
from hashlib import md5
from datetime import datetime, timedelta
from conf import config
from orm import crud
from orm.db_model import users
from sqlalchemy.orm import Session
from orm.dependencies import get_db


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
    user_password: str,
    expire_time: int = 30,
    secret_key: str = config.JWT_SECRET_KEY,
):
    token_dict = {
        "expire_time": (datetime.now() + timedelta(minutes=expire_time)).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "email_address": email_address,
        "user_password": user_password,
    }
    jwt_token = jwt.encode(token_dict, secret_key, algorithm="HS256")
    return jwt_token


def verify_user_token(db: Session, token: str, secret_key: str = config.JWT_SECRET_KEY):
    try:
        token_dict = jwt.decode(jwt=token, key=secret_key, algorithms="HS256")
        email_address = token_dict.get("email_address", "")
        user_password = token_dict.get("user_password", "")
        expire_time = token_dict.get("expire_time", "")
        if not email_address or not user_password or not expire_time:
            return False, email_address, "用户认证错误，请重新登录"
        if expire_time < datetime.now().strftime("%Y-%m-%d %H:%M:%S"):
            return False, email_address, "token已过期"
        user_dict = crud.get_user(db, [users.User.email_address == email_address])
        if not user_dict:
            return False, email_address, "无用户，请重新登录"
        if user_dict.user_password != user_password:
            return False, email_address, "用户密码错误，请重新登陆"
        return True, email_address, "校验正确"
    except jwt.ExpiredSignatureError as e:
        print(e)
        return False, "", "登录时间过长，请重新登录"
    except jwt.exceptions.PyJWTError as e:
        print(e)
        return False, "", "用户认证错误，请重新登录"


if __name__ == "__main__":
    pass
    # salt, md5_pwd = create_md5('123456')
    # print(salt, md5_pwd)
    # salt = create_salt(24)
    # print(salt)
    # jwt_token = create_token(email_address="test", user_password='12312', expire_time=30)
    # print(jwt_token)
    verify_result, email_address, verify_message = verify_user_token(
        db=next(get_db()),
        token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHBpcmVfdGltZSI6IjIwMjMtMDctMjQgMTc6MDA6MjgiLCJlbWFpbF9hZGRyZXNzIjoiNjE5NTg5MzUxQHFxLmNvbSIsInVzZXJfcGFzc3dvcmQiOiI1MGVmYmRkODU3ZWE0YWZmNmRmMGY0NmFiNGU5ZDU3OCJ9.WYcdYoBHXPFC7-Z8wtz5lK14KvJ96gSqJMAqFQoZlvY",
    )
