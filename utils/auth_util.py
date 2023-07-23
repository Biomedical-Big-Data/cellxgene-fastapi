import jwt
from random import Random
from hashlib import md5
from datetime import datetime, timedelta
from conf import config


def create_salt(length=8):
    salt = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    len_chars = len(chars) - 1
    random = Random()
    for i in range(length):
        salt += chars[random.randint(0, len_chars)]
    return salt


def create_md5_password(password):
    salt = create_salt()
    md5_pwd = md5()
    md5_pwd.update((password + salt).encode('utf-8'))
    return salt, md5_pwd.hexdigest()


def create_token(user_name: str, expire_time: int, secret_key: str = config.JWT_SECRET_KEY):
    token_dict = {
        'exp': datetime.now() + timedelta(minutes=expire_time),
        'username': user_name
    }
    jwt_token = jwt.encode(token_dict,
                           secret_key,
                           algorithm="HS256")
    return jwt_token


if __name__ == "__main__":
    pass
    # salt, md5_pwd = create_md5('123456')
    # print(salt, md5_pwd)
    # salt = create_salt(24)
    # print(salt)
    jwt_token = create_token(user_name='test', expire_time=30)
    print(jwt_token)
