import re
from fastapi import APIRouter, Depends, HTTPException, status
from orm.dependencies import get_db
from orm.schema import user_model
from orm.schema.response import ResponseMessage
from orm import crud
from sqlalchemy.orm import Session
from orm.db_model import users
from utils import auth_util, mail_util
from conf import config


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/register", response_model=ResponseMessage, status_code=status.HTTP_200_OK
)
async def register(user: user_model.UserModel, db: Session = Depends(get_db)):
    if len(user.user_password) < 6 or len(user.user_password) > 16:
        return ResponseMessage(
            status="0201", data="密码应大于6位或小于16位", message="密码应大于6位或小于16位"
        )
    if not re.search("^[1-9a-zA-Z]", user.user_password):
        return ResponseMessage(
            status="0201", data="密码应包含数字及大小写字母", message="密码应包含数字及大小写字母"
        )
    if crud.get_user(db, [users.User.email_address == user.email_address]):
        return ResponseMessage(status="0201", data="此邮箱已有账号", message="此邮箱已有账号")
    if crud.get_user(db, [users.User.user_name == user.user_name]):
        return ResponseMessage(status="0201", data="用户名已存在", message="用户名已存在")
    salt, jwt_user_password = auth_util.create_md5_password(
        salt=None, password=user.user_password
    )
    crud.create_user(
        db,
        users.User(
            user_name=user.user_name,
            email_address=user.email_address,
            salt=salt,
            user_password=jwt_user_password,
            verify_state=config.NOT_VERIFY_STATE,
        ),
    )
    token = auth_util.create_token(
        email_address=user.email_address, user_password=jwt_user_password
    )
    verify_url = "{}".format(config.VERIFY_URL + token)
    send_mail_result = mail_util.send_mail(
        user_name=user.user_name, verify_url=verify_url, to_list=user.email_address
    )
    if send_mail_result:
        return ResponseMessage(
            status="0000", data="注册成功，请到邮箱点击验证链接", message="注册成功，请到邮箱点击验证链接"
        )
    else:
        return ResponseMessage(
            status="0201", data="注册成功，验证邮件发送失败，请点击重新发送", message="注册成功，验证邮件发送失败，请点击重新发送"
        )


@router.get(
    "/email/verify", response_model=ResponseMessage, status_code=status.HTTP_200_OK
)
async def verify_user_email(token: str, db: Session = Depends(get_db)):
    verify_result, email_address, verify_message = auth_util.verify_user_token(
        db, token
    )
    if not verify_result:
        return ResponseMessage(
            status="0201", data=verify_message, message="verify_message"
        )
    crud.update_user(
        db,
        [users.User.email_address == email_address],
        {"verify_state": config.VERIFY_STATE},
    )
    return ResponseMessage(status="0000", data="邮箱校验成功", message="邮箱校验成功")


@router.get("/login", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def user_login(
    email_address: str, user_password: str, db: Session = Depends(get_db)
):
    user_dict = crud.get_user(db, [users.User.email_address == email_address])
    salt, jwt_user_password = auth_util.create_md5_password(
        salt=user_dict.salt, password=user_password
    )
    if jwt_user_password == user_dict.user_password:
        token = auth_util.create_token(
            email_address=email_address,
            user_password=user_password,
            expire_time=60 * 24,
        )
        return_dict = user_dict.to_dict()
        return_dict["token"] = token
        return ResponseMessage(status="0000", data=return_dict, message="登录成功")
    else:
        return ResponseMessage(status="0201", data="登录失败，密码错误", message="登录失败，密码错误")
