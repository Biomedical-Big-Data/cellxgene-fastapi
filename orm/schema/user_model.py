from pydantic import BaseModel


class UserModel(BaseModel):
    user_name: str
    user_password: str
    organization: str
    email_address: str

    def to_dict(self):
        return {
            "user_name": self.user_name,
            "email_address": self.email_address,
            "organization": self.organization,
            "user_password": self.user_password
        }


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
