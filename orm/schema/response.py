from pydantic import BaseModel
from typing import Any, List
from orm.schema import project_model


class ResponseMessage(BaseModel):
    status: str
    data: Any
    message: str


class ResponseBiosampleModel(BaseModel):
    status: str
    data: List[project_model.BiosampleModel]
    message: str


class ResponseCellModel(BaseModel):
    status: str
    data: List[project_model.CellTypeModel]
    message: str


class ResponseGeneModel(BaseModel):
    status: str
    data: List[project_model.GeneModel]
    message: str
