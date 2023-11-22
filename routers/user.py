import re
from typing import Union

from fastapi import APIRouter, Depends, status, Body
from fastapi.responses import HTMLResponse
from orm.dependencies import get_db, get_current_user
from orm.schema import user_model
from orm.schema.exception_model import USER_NOT_VERIFY_EXCEPTION, USERBLOCK_EXCEPTION
from orm.schema.response import ResponseMessage, ResponseUserModel
from orm import crud
from sqlalchemy.orm import Session
from orm.db_model import cellxgene
from utils import auth_util, mail_util
from conf import config
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={200: {"description": {"status": "0000", "data": {}, "message": "failed"}}},
)


@router.post(
    "/register", response_model=ResponseMessage, status_code=status.HTTP_200_OK
)
async def register(
    user: user_model.RegisterUserModel, db: Session = Depends(get_db)
) -> ResponseMessage:
    if len(user.user_password) < 6 or len(user.user_password) > 16:
        return ResponseMessage(status="0201", data={}, message="The password should be more than 6 characters or less than 16 characters")
    if not re.search("^[1-9a-zA-Z]", user.user_password):
        return ResponseMessage(status="0201", data={}, message="The password should contain numbers and uppercase and lowercase letters")
    if crud.get_user(db, [cellxgene.User.email_address == user.email_address]).first():
        return ResponseMessage(status="0201", data={}, message="This email already has an account")
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
    token = auth_util.create_token(
        email_address=user.email_address, expire_time=config.JWT_VERIFY_EXPIRE_TIME
    )
    verify_url = "{}".format(config.VERIFY_URL + token)
    mail_template = mail_util.verify_mail_template(
        user_name=user.user_name, verify_url=verify_url
    )
    send_mail_result = mail_util.send_mail(
        mail_template=mail_template, subject="Confirm your account activation", to_list=user.email_address
    )
    if send_mail_result:
        return ResponseMessage(status="0000", data={}, message="Registration is successful, please click the verification link in email")
    else:
        return ResponseMessage(status="0201", data={}, message="Registration success, verification email failed to send, please click resend")


@router.post("/login", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def user_login(
    login_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> ResponseMessage:
    user_info_model = crud.get_user(
        db, [cellxgene.User.email_address == login_data.username]
    ).first()
    if not user_info_model:
        return ResponseMessage(status="0201", data={}, message="User name error")
    if user_info_model.state == config.UserStateConfig.USER_STATE_NOT_VERIFY:
        raise USER_NOT_VERIFY_EXCEPTION
    if user_info_model.state == config.UserStateConfig.USER_STATE_BLOCK:
        raise USERBLOCK_EXCEPTION
    salt, jwt_user_password = auth_util.create_md5_password(
        salt=user_info_model.salt, password=login_data.password
    )
    if jwt_user_password == user_info_model.user_password:
        token = auth_util.create_token(
            email_address=login_data.username,
            expire_time=config.JWT_LOGIN_EXPIRE_TIME,
        )
        return ResponseMessage(
            status="0000",
            data={
                "access_token": token,
                "token_type": "bearer",
                "user_info": user_info_model.to_dict(),
            },
            message="Login successful",
        )
    else:
        return ResponseMessage(status="0201", data={}, message="Login failed, password is incorrect")


@router.get("/me", response_model=ResponseUserModel, status_code=status.HTTP_200_OK)
async def get_user_info(
    db: Session = Depends(get_db),
    current_user_email_address: str = Depends(get_current_user),
) -> ResponseMessage:
    user_info_model = crud.get_user(
        db, [cellxgene.User.email_address == current_user_email_address]
    ).first()
    return ResponseMessage(status="0000", data=user_info_model, message="success")


@router.post("/me/edit", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def edit_user_info(
    user_info: user_model.EditInfoUserModel = Body(),
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
) -> ResponseMessage:
    if not user_info:
        return ResponseMessage(status="0201", data={}, message="No updated content")
    if user_info.email_address:
        check_user_dict = crud.get_user(
            db, [cellxgene.User.email_address == user_info.email_address]
        ).first()
        if check_user_dict:
            return ResponseMessage(status="0201", data={}, message="This email already has an account")
    update_user_dict = {}
    for key, value in user_info.to_dict().items():
        if value:
            update_user_dict[key] = value
    if user_info.user_password:
        salt, jwt_user_password = auth_util.create_md5_password(
            salt=None, password=user_info.user_password
        )
        update_user_dict["user_password"] = jwt_user_password
        update_user_dict["salt"] = salt
    crud.update_user(
        db,
        [cellxgene.User.email_address == current_user_email_address],
        update_user_dict,
    )
    return ResponseMessage(status="0000", data={}, message="The user information is updated successful")


@router.get(
    "/email/verify", response_model=ResponseMessage, status_code=status.HTTP_200_OK
)
async def verify_user_email(
    token: str, db: Session = Depends(get_db)
) -> ResponseMessage:
    email_address = auth_util.check_token_for_verify_email(db=db, token=token)
    crud.update_user(
        db,
        [cellxgene.User.email_address == email_address],
        {"state": config.UserStateConfig.USER_STATE_VERIFY},
    )
    return ResponseMessage(status="0000", data={}, message="Email verification successful")


@router.post(
    "/password/reset/mail/send",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
)
async def send_reset_user_password_mail(
    user: user_model.PasswordResetModel, db: Session = Depends(get_db)
) -> ResponseMessage:
    user_dict = crud.get_user(
        db, [cellxgene.User.email_address == user.email_address]
    ).first()
    if not user_dict:
        return ResponseMessage(status="0201", data={}, message="User name error")
    token = auth_util.create_token(
        email_address=user_dict.email_address,
        expire_time=config.JWT_RESET_PASSWORD_EXPIRE_TIME,
    )
    reset_password_url = "{}".format(config.RESET_PASSWORD_URL + token)
    mail_template = mail_util.reset_password_mail_template(
        user_name=user_dict.user_name, reset_password_url=reset_password_url
    )
    send_mail_result = mail_util.send_mail(
        mail_template=mail_template, subject="Reset your password", to_list=user_dict.email_address
    )
    if send_mail_result:
        return ResponseMessage(
            status="0000",
            data={},
            message="Reset password link has been sent to your email, please complete reset within half an hour",
        )
    else:
        return ResponseMessage(status="0201", data={}, message="Reset password email failed to send, please click resend")


@router.post(
    "/password/reset",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
)
async def reset_user_password(
    password: str = Body(), token: str = Body(), db: Session = Depends(get_db)
) -> ResponseMessage:
    email_address = auth_util.check_token_for_verify_email(db=db, token=token)
    if len(password) < 6 or len(password) > 16:
        return ResponseMessage(status="0201", data={}, message="The password should be more than 6 characters or less than 16 characters")
    if not re.search("^[1-9a-zA-Z]", password):
        return ResponseMessage(status="0201", data={}, message="The password should contain numbers and uppercase and lowercase letters")
    salt, jwt_user_password = auth_util.create_md5_password(
        salt=None, password=password
    )
    try:
        crud.update_user(
            db,
            [cellxgene.User.email_address == email_address],
            {"user_password": jwt_user_password, "salt": salt},
        )
        return ResponseMessage(
            status="0000",
            data={},
            message="Reset password successful",
        )
    except:
        return ResponseMessage(
            status="0201",
            data={},
            message="Reset password failed",
        )
