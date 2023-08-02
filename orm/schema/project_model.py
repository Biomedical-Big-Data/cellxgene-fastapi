from pydantic import BaseModel


class CellProportion(BaseModel):
    cell_proportion: str
    cell_number: int

    class Config:
        org_mode = True


class GeneExpression(BaseModel):
    cell_proportion_expression_the_gene: float

    class Config:
        org_mode = True


class ProjectMeta(BaseModel):
    title: str

    class Config:
        org_mode = True


class DonorMeta(BaseModel):
    sex: str

    class Config:
        org_mode = True


class Species(BaseModel):
    species: str

    class Config:
        org_mode = True


class ResponseProjectModel(BaseModel):
    cell_type: str
    project_title: ProjectMeta
    disease: str
    platform: str
    species: str
    organ: str
    sex: DonorMeta
    cell_proportion: CellProportion | None = None
    cell_proportion_expression_the_gene: GeneExpression | None = None

    class Config:
        org_mode = True


class SearchProjectModel(BaseModel):
    search_type: str
    organ: str | None
    species_id: int | None
    cell_id: int | None
    gene_symbol: str | None
