import re
from fastapi import APIRouter, Depends, HTTPException
from orm.dependencies import get_db
from orm.schema import user_model
from orm.schema.response import ResponseMessage
from orm import crud
from sqlalchemy.orm import Session
from orm.db_model import users
from utils.send_mail import send_mail


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/register", response_model=ResponseMessage, status_code=200)
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
        return ResponseMessage(status="0201", data="用户已存在", message="用户已存在")

    return ResponseMessage(status="0000", data="注册成功", message="注册成功")


@router.get("/login")
async def user_login(user: user_model.UserModel):
    pass
