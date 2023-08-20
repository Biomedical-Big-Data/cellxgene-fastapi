from pydantic import BaseModel
from datetime import datetime


class UserModel(BaseModel):
    id: int
    user_name: str
    email_address: str
    organization: str
    # salt: str
    # user_password: str
    state: int
    role: int
    create_at: datetime
    update_at: datetime

    class Config:
        org_mode = True


class RegisterUserModel(BaseModel):
    user_name: str
    user_password: str
    organization: str
    email_address: str


class PasswordResetModel(BaseModel):
    email_address: str


class EditInfoUserModel(BaseModel):
    user_name: str
    user_password: str | None
    organization: str
    email_address: str

    def to_dict(self):
        return {
            "user_name": self.user_name,
            "email_address": self.email_address,
            "organization": self.organization,
            "user_password": self.user_password,
        }


class AdminEditInfoUserModel(BaseModel):
    user_name: str
    email_address: str
    organization: str
    user_password: str
    state: int
    role: int

    def to_dict(self):
        return {
            "user_name": self.user_name,
            "email_address": self.email_address,
            "organization": self.organization,
            "user_password": self.user_password,
            "state": self.state,
            "role": self.role,
        }
