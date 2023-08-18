from typing import List
from orm.schema.project_model import (
    BiosampleModel,
    ProjectModel,
    DonorModel,
    SpeciesModel,
    AnalysisModel,
    CellClusterProportionModel,
    CellTypeModel,
    GeneModel,
    GeneExpression,
)
from orm.schema.user_model import UserModel


class BiosampleModelRelation(BiosampleModel):
    biosample_project_meta: List[ProjectModel]
    biosample_donor_meta: DonorModel
    biosample_species_meta: SpeciesModel

    class Config:
        org_mode = True


class AnalysisRelation(AnalysisModel):
    analysis_project_meta: ProjectModel
    analysis_biosample_meta: List[BiosampleModel]

    class Config:
        org_mode = True


class CellClusterProportionRelation(CellClusterProportionModel):
    cell_proportion_analysis_meta: AnalysisRelation

    class Config:
        org_mode = True


class CellTypeRelation(CellTypeModel):
    cell_type_species_meta: SpeciesModel
    cell_type_proportion_meta: List[CellClusterProportionRelation]

    class Config:
        org_mode = True


class GeneExpressionRelation(GeneExpression):
    gene_expression_proportion_meta: CellClusterProportionRelation

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
