from pydantic import BaseModel


class CellProportion(BaseModel):
    cell_proportion: str
    cell_number: int

    class Config:
        org_mode = True


class GeneExpression(BaseModel):
    cell_proportion_expression_the_gene: float

    class Config:
        org_code = True


class ProjectModel(BaseModel):
    result: int
    cell_type: str
    project_title: str
    disease: str
    platform: str
    species: str
    organ: str
    sex: str
    cell_proportion: CellProportion | None = None
    cell_proportion_expression_the_gene: GeneExpression | None = None

    class Config:
        org_mode = True


