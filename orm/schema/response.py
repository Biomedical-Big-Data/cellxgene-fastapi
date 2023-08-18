from pydantic import BaseModel
from typing import Any, List, Union
from orm.schema import project_relation_model


class ResponseMessage(BaseModel):
    status: str
    data: Any
    message: str

    def to_dict(self):
        return {
            "status": self.status,
            "data": self.data,
            "message": self.message
        }


class ResponseBiosampleModel(BaseModel):
    status: str
    data: List[project_relation_model.BiosampleModelRelation]
    message: str


class ResponseCellModel(BaseModel):
    status: str
    data: List[project_relation_model.CellTypeRelation]
    message: str


class ResponseGeneModel(BaseModel):
    status: str
    data: List[project_relation_model.GeneRelation]
    message: str


class ResponseUserModel(BaseModel):
    status: str
    data: Union[project_relation_model.UserProjectRelation, str]
    message: str
