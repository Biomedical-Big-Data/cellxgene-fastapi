from typing import List, Union
from orm.schema.project_model import (
    BiosampleModel,
    ProjectModel,
    DonorModel,
    SpeciesModel,
    AnalysisModel,
    CellClusterProportionModel,
    CellTypeModel,
    GeneModel,
    CellClusterGeneExpressionModel,
    ProjectBiosampleModel,
    BiosampleAnalysisModel,
)
from orm.schema.user_model import UserModel, ProjectUserModel


class ProjectBiosampleRelation(ProjectBiosampleModel):
    project_biosample_biosample_meta: BiosampleModel

    class Config:
        org_mode = True


class ProjectUserRelation(ProjectUserModel):
    project_user_user_meta: UserModel


class ProjectRelation(ProjectModel):
    project_analysis_meta: Union[List[AnalysisModel], None]
    project_user_meta: Union[UserModel, None]
    project_project_biosample_meta: Union[List[ProjectBiosampleRelation], None]
    project_project_user_meta: Union[List[ProjectUserRelation], None]

    class Config:
        org_mode = True


class BiosampleProjectRelation(ProjectBiosampleModel):
    project_biosample_project_meta: ProjectModel

    class Config:
        org_mode = True


class BiosampleModelRelation(BiosampleModel):
    biosample_project_biosample_meta: List[BiosampleProjectRelation]
    biosample_donor_meta: Union[DonorModel, None]
    biosample_species_meta: SpeciesModel

    class Config:
        org_mode = True


class BiosampleModelRelationForCell(BiosampleModel):
    biosample_donor_meta: DonorModel
    biosample_species_meta: SpeciesModel

    class Config:
        org_mode = True


class BiosampleAnalysisRelation(BiosampleAnalysisModel):
    biosample_analysis_biosample_meta: BiosampleModelRelationForCell

    class Config:
        org_mode = True


class AnalysisRelation(AnalysisModel):
    analysis_project_meta: ProjectModel
    analysis_biosample_analysis_meta: List[BiosampleAnalysisRelation]

    class Config:
        org_mode = True


class CellClusterProportionRelation(CellClusterProportionModel):
    cell_proportion_analysis_meta: AnalysisRelation
    proportion_cell_type_meta: CellTypeModel

    class Config:
        org_mode = True


class CellClusterProportionRelationForGraph(CellClusterProportionModel):
    proportion_cell_type_meta: CellTypeModel

    class Config:
        org_mode = True


class CellTypeRelation(CellTypeModel):
    cell_type_species_meta: SpeciesModel
    cell_type_proportion_meta: List[CellClusterProportionRelation]

    class Config:
        org_mode = True


class GeneExpressionRelation(CellClusterGeneExpressionModel):
    gene_expression_proportion_meta: CellClusterProportionRelation

    class Config:
        org_mode = True


class GeneExpressionRelationForGraph(CellClusterGeneExpressionModel):
    gene_expression_proportion_meta: CellClusterProportionRelationForGraph

    class Config:
        org_mode = True


class GeneRelation(GeneModel):
    gene_species_meta: SpeciesModel
    gene_gene_expression_meta: List[GeneExpressionRelation]

    class Config:
        org_mode = True


class UserProjectRelation(UserModel):
    user_project_meta: List[ProjectModel]

    class Config:
        org_mode = True
