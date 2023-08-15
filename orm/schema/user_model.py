from pydantic import BaseModel


class RegisterUserModel(BaseModel):
    user_name: str
    user_password: str
    organization: str
    email_address: str


class FiterUserModel(BaseModel):
    user_name: str | None
    email_address: str | None


class SearchUserListModel(BaseModel):
    user_name: str
    organization: str
    email_address: str
    create_time: str


class LoginUserModel(BaseModel):
    email_address: str
    user_password: str


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
