from pydantic import BaseModel
from typing import Any, List, Union
from orm.schema import project_relation_model


class ResponseMessage(BaseModel):
    status: str
    data: Any
    message: Any

    def to_dict(self):
        return {"status": self.status, "data": self.data, "message": self.message}


class ProjectListModel(BaseModel):
    project_list: Union[List[project_relation_model.GeneRelation], List[project_relation_model.CellTypeRelation], List[project_relation_model.BiosampleModelRelation]]
    total: int
    page: int
    page_size: int


class ResponseProjectModel(BaseModel):
    status: str
    data: ProjectListModel
    message: str


class UserInfoListModel(BaseModel):
    user_list: Union[
            project_relation_model.UserProjectRelation,
            List[project_relation_model.UserProjectRelation],
            str
        ]
    total: int
    page: int
    page_size: int


class ResponseUserModel(BaseModel):
    status: str
    data: Union[
            UserInfoListModel,
            project_relation_model.UserProjectRelation,
            List[project_relation_model.UserProjectRelation],
            str
        ]
    message: str

