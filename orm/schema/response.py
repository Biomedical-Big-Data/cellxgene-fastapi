from pydantic import BaseModel
from typing import Any, List
from orm.schema import project_relation_model


class ResponseMessage(BaseModel):
    status: str
    data: Any
    message: str


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
