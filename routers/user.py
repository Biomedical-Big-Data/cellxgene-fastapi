import re
from fastapi import APIRouter, Depends, HTTPException, status, Header, Body
from fastapi.responses import HTMLResponse
from orm.dependencies import get_db, get_current_user
from orm.schema import user_model
from orm.schema.response import ResponseMessage
from orm import crud
from sqlalchemy.orm import Session
from orm.db_model import cellxgene
from utils import auth_util, mail_util
from conf import config


router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/register", response_model=ResponseMessage, status_code=status.HTTP_200_OK
)
async def register(user: user_model.RegisterUserModel, db: Session = Depends(get_db)):
    if len(user.user_password) < 6 or len(user.user_password) > 16:
        return ResponseMessage(
            status="0201", data="密码应大于6位或小于16位", message="密码应大于6位或小于16位"
        )
    if not re.search("^[1-9a-zA-Z]", user.user_password):
        return ResponseMessage(
            status="0201", data="密码应包含数字及大小写字母", message="密码应包含数字及大小写字母"
        )
    if crud.get_user(db, [cellxgene.User.email_address == user.email_address]).first():
        return ResponseMessage(status="0201", data="此邮箱已有账号", message="此邮箱已有账号")
    salt, jwt_user_password = auth_util.create_md5_password(
        salt=None, password=user.user_password
    )
    crud.create_user(
        db,
        cellxgene.User(
            user_name=user.user_name,
            email_address=user.email_address,
            salt=salt,
            organization=user.organization,
            user_password=jwt_user_password,
            state=config.UserStateConfig.USER_STATE_NOT_VERIFY,
            role=config.UserRole.USER_ROLE_FORMAL,
        ),
    )
    token = auth_util.create_token(email_address=user.email_address)
    verify_url = "{}".format(config.VERIFY_URL + token)
    mail_template = mail_util.verify_mail_template(
        user_name=user.user_name, verify_url=verify_url
    )
    send_mail_result = mail_util.send_mail(
        mail_template=mail_template, subject="账户验证邮件", to_list=user.email_address
    )
    if send_mail_result:
        return ResponseMessage(
            status="0000", data="注册成功，请到邮箱点击验证链接", message="注册成功，请到邮箱点击验证链接"
        )
    else:
        return ResponseMessage(
            status="0201", data="注册成功，验证邮件发送失败，请点击重新发送", message="注册成功，验证邮件发送失败，请点击重新发送"
        )


@router.post("/login", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def user_login(user: user_model.LoginUserModel, db: Session = Depends(get_db)):
    user_info_model = crud.get_user(
        db, [cellxgene.User.email_address == user.email_address]
    ).first()
    if not user_info_model:
        return ResponseMessage(status="0201", data="用户名错误", message="用户名错误")
    salt, jwt_user_password = auth_util.create_md5_password(
        salt=user_info_model.salt, password=user.user_password
    )
    if jwt_user_password == user_info_model.user_password:
        token = auth_util.create_token(
            email_address=user.email_address,
            expire_time=60 * 24,
        )
        user_info_dict = user_info_model.to_dict()
        user_info_dict["token"] = token
        return ResponseMessage(status="0000", data=user_info_dict, message="登录成功")
    else:
        return ResponseMessage(status="0201", data="登录失败，密码错误", message="登录失败，密码错误")


@router.get("/list", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def get_user_list():
    pass


@router.get("/info", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def get_user_info(email_address: str, db: Session = Depends(get_db)):
    user_info_model = crud.get_user(
        db, [cellxgene.User.email_address == email_address]
    ).first()
    return ResponseMessage(
        status="0000", data=user_info_model.to_dict(), message="success"
    )


@router.post(
    "/info/edit", response_model=ResponseMessage, status_code=status.HTTP_200_OK
)
async def edit_user_info(
    token: str = Header(),
    user_info: user_model.EditInfoUserModel = Body(),
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
):
    user_dict = crud.get_user(
        db, [cellxgene.User.email_address == current_user_email_address]
    ).first()
    if user_info.email_address != user_dict.email_address:
        check_user_dict = crud.get_user(
            db, [cellxgene.User.email_address == user_info.email_address]
        ).first()
        if check_user_dict:
            return ResponseMessage(status="0201", data="此邮箱已有账号", message="此邮箱已有账号")
    update_user_dict = user_info.to_dict()
    if user_info.user_password:
        salt, jwt_user_password = auth_util.create_md5_password(
            salt=user_dict.salt, password=user_info.user_password
        )
        update_user_dict["user_password"] = jwt_user_password
    crud.update_user(
        db,
        [cellxgene.User.email_address == current_user_email_address],
        update_user_dict,
    )
    return ResponseMessage(status="0000", data="用户信息更新成功", message="用户信息更新成功")


@router.get(
    "/email/verify", response_model=ResponseMessage, status_code=status.HTTP_200_OK
)
async def verify_user_email(token: str, db: Session = Depends(get_db)):
    email_address = auth_util.check_token_for_verify_email(db=db, token=token)
    crud.update_user(
        db,
        [cellxgene.User.email_address == email_address],
        {"state": config.UserStateConfig.USER_STATE_VERIFY},
    )
    return ResponseMessage(status="0000", data="邮箱校验成功", message="邮箱校验成功")


@router.post(
    "/password/reset/mail/send",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
)
async def send_reset_user_password_mail(
    user: user_model.PasswordResetModel, db: Session = Depends(get_db)
):
    user_dict = crud.get_user(
        db, [cellxgene.User.email_address == user.email_address]
    ).first()
    if not user_dict:
        return ResponseMessage(status="0201", data="用户名错误", message="用户名错误")
    token = auth_util.create_token(email_address=user_dict.email_address)
    reset_password_url = "{}".format(config.RESET_PASSWORD_URL + token)
    mail_template = mail_util.reset_password_mail_template(
        user_name=user_dict.user_name, reset_password_url=reset_password_url
    )
    send_mail_result = mail_util.send_mail(
        mail_template=mail_template, subject="重置密码邮件", to_list=user_dict.email_address
    )
    if send_mail_result:
        return ResponseMessage(
            status="0000",
            data="重置密码链接已发送至您的邮箱，请在半小时内完成重置",
            message="重置密码链接已发送至您的邮箱，请在半小时内完成重置",
        )
    else:
        return ResponseMessage(
            status="0201", data="重置密码邮件发送失败，请点击重新发送", message="重置密码邮件发送失败，请点击重新发送"
        )


@router.get(
    "/password/reset/check",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
async def get_reset_password_template(token: str, db: Session = Depends(get_db)):
    email_address = auth_util.check_token_for_verify_email(db=db, token=token)
    return ResponseMessage(status="0000", data="密码修改成功", message="密码修改成功")


@router.post(
    "/password/reset",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
)
async def reset_user_password(
    reset_password_model: user_model.LoginUserModel, db: Session = Depends(get_db)
):
    if (
        len(reset_password_model.user_password) < 6
        or len(reset_password_model.user_password) > 16
    ):
        return ResponseMessage(
            status="0201", data="密码应大于6位或小于16位", message="密码应大于6位或小于16位"
        )
    if not re.search("^[1-9a-zA-Z]", reset_password_model.user_password):
        return ResponseMessage(
            status="0201", data="密码应包含数字及大小写字母", message="密码应包含数字及大小写字母"
        )
    user_dict = crud.get_user(
        db, [cellxgene.User.email_address == reset_password_model.email_address]
    ).first()
    if not user_dict:
        return ResponseMessage(status="0201", data="用户不存在", message="用户不存在")
    salt, jwt_user_password = auth_util.create_md5_password(
        salt=user_dict.salt, password=reset_password_model.user_password
    )
    res = crud.update_user(
        db,
        [cellxgene.User.email_address == reset_password_model.email_address],
        {"user_password": jwt_user_password},
    )
    print(type(res), res)
    return ResponseMessage(
        status="0000",
        data="重置成功",
        message="重置成功",
    )
