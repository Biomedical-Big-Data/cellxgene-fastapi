from pydantic import BaseModel


class UserModel(BaseModel):
    user_name: str
    user_password: str
    email_address: str


class FiterUserModel(BaseModel):
    user_name: str | None
    email_address: str | None
