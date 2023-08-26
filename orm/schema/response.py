from pydantic import BaseModel
from typing import Any, List, Union
from orm.schema import project_relation_model, project_model


class ResponseMessage(BaseModel):
    status: str
    data: Any
    message: Any

    def to_dict(self):
        return {"status": self.status, "data": self.data, "message": self.message}


class CellTypeListModel(BaseModel):
    cell_type_list: List[project_model.CellTypeModel]
    total: int
    page: int
    page_size: int


class GeneListModel(BaseModel):
    gene_list: List[project_model.GeneModel]
    total: int
    page: int
    page_size: int


class ProjectListModel(BaseModel):
    project_list: Union[
        List[project_relation_model.GeneExpressionRelation],
        List[project_relation_model.CellClusterProportionRelation],
        List[project_relation_model.BiosampleModelRelation],
        List[project_relation_model.ProjectRelation],
    ]
    total: int
    page: int
    page_size: int


class ResponseProjectListModel(BaseModel):
    status: str
    data: Union[ProjectListModel, CellTypeListModel, GeneListModel]
    message: str


class UserInfoListModel(BaseModel):
    user_list: Union[
        project_relation_model.UserProjectRelation,
        List[project_relation_model.UserProjectRelation],
        str,
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
        str,
    ]
    message: str


class ResponseProjectDetailModel(BaseModel):
    status: str
    data: Union[
        project_relation_model.ProjectRelation,
        ProjectListModel,
        str,
    ]
    message: str
