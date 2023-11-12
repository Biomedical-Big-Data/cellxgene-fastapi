from pydantic import BaseModel
from typing import Any, List, Union
from orm.schema import project_relation_model, project_model, user_model


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


class SpeciesListModel(BaseModel):
    species_list: List[project_model.SpeciesModel]
    total: int
    page: int
    page_size: int


class DonorListModel(BaseModel):
    donor_list: List[project_model.DonorModel]
    total: int
    page: int
    page_size: int


class H5adListModel(BaseModel):
    h5ad_list: List[project_model.FileLibraryModel]
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


class ProjectListForSearch(BaseModel):
    project_list: list
    cell_type_list: Union[List[project_model.CellTypeModel], None] = None
    total: int
    page: int
    page_size: int


class ResponseProjectListModel(BaseModel):
    status: str
    data: Union[
        ProjectListForSearch,
        ProjectListModel,
        CellTypeListModel,
        GeneListModel,
        DonorListModel,
        SpeciesListModel,
        H5adListModel,
        List[project_model.SpeciesModel],
    ]
    message: str


class UserInfoListModel(BaseModel):
    user_list: Union[
        user_model.UserModel,
        List[user_model.UserModel],
        str,
        dict,
    ]
    total: int
    page: int
    page_size: int


class ResponseUserModel(BaseModel):
    status: str
    data: Union[
        UserInfoListModel,
        user_model.UserModel,
        List[user_model.UserModel],
        str,
        dict,
    ]
    message: str


class ResponseProjectDetailModel(BaseModel):
    status: str
    data: Union[
        project_relation_model.ProjectRelation,
        ProjectListModel,
        project_relation_model.AnalysisRelation,
        List[project_relation_model.CellClusterProportionRelationForGraph],
        List[project_model.PathwayScoreModel],
        List[project_model.CellTaxonomyModel],
        str,
        dict,
    ]
    message: str
