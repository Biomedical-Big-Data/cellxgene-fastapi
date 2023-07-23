from random import Random
from hashlib import md5


def create_salt(length=8):
    salt = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    len_chars = len(chars) - 1
    random = Random()
    for i in range(length):
        salt += chars[random.randint(0, len_chars)]
    return salt


def create_md5(password):
    salt = create_salt()
    md5_pwd = md5()
    md5_pwd.update((password + salt).encode('utf-8'))
    return salt, md5_pwd.hexdigest()


if __name__ == "__main__":
    salt, md5_pwd = create_md5('123456')
    print(salt, md5_pwd)