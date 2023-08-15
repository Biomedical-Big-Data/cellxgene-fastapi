from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Header,
    Body,
    File,
    UploadFile,
)
from fastapi.responses import HTMLResponse
from orm.dependencies import get_db
from orm.schema.project_model import ProjectModel
from orm.schema.response import (
    ResponseMessage,
    ResponseBiosampleModel,
    ResponseCellModel,
    ResponseGeneModel,
)
from orm import crud
from sqlalchemy.orm import Session
from orm.db_model import cellxgene
from utils import auth_util, mail_util
from conf import config
from typing import List, Union
from io import BytesIO
import pandas as pd
from sqlalchemy import and_, or_


router = APIRouter(
    prefix="/project",
    tags=["project"],
    responses={404: {"description": "Not found"}},
)


@router.get("/list/{project_id}", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def get_project_list(
    project_id: int,
    db: Session = Depends(get_db)
):
    project_info_model = crud.get_project_detail(db=db, project_id=project_id)
    if not project_info_model:
        return ResponseMessage(status="0201", data="无此项目", message="无此项目")
    return ResponseMessage(status="0000", data=project_info_model.to_dict(), message="ok")


@router.post("/create", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def create_project(
    title: str = Body(),
    description: str = Body(),
    # h5ad_file: UploadFile | None = Body(),
    tag: str = Body(),
    project_status: int = Body(),
    db: Session = Depends(get_db)
):
    insert_project_model = cellxgene.ProjectMeta(
        title=title,
        description=description
    )
    project_id = crud.create_project(db=db, insert_project_model=insert_project_model)
    insert_analysis_model = cellxgene.Analysis(
        project_id=project_id,
        project_status=project_status
    )
    crud.create_analysis(db=db, insert_analysis_model=insert_analysis_model)
    return ResponseMessage(status="0000", data="项目创建成功", message="项目创建成功")


@router.get(
    "/list/by/sample",
    response_model=ResponseBiosampleModel,
    status_code=status.HTTP_200_OK,
)
async def get_project_list_by_sample(
    organ: Union[str, None] = None,
    species_id: Union[int, None] = None,
    external_sample_accesstion: Union[str, None] = None,
    disease: Union[str, None] = None,
    development_stage: Union[str, None] = None,
    page: int = 0,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    filter_list = []
    if organ:
        filter_list.append(cellxgene.BioSampleMeta.organ == organ)
    if species_id:
        filter_list.append(cellxgene.BioSampleMeta.species_id == species_id)
    if external_sample_accesstion:
        filter_list.append(
            cellxgene.BioSampleMeta.external_sample_accesstion
            == external_sample_accesstion
        )
    if disease:
        filter_list.append(cellxgene.BioSampleMeta.disease.like("%{}%".format(disease)))
    if development_stage:
        filter_list.append(
            cellxgene.BioSampleMeta.development_stage.like(
                "%{}%".format(development_stage)
            )
        )
    biosample_list = crud.get_project_by_sample(
        db=db, filters=filter_list, page=page, page_size=page_size
    )
    return ResponseMessage(status="0000", data=biosample_list, message="ok")


@router.get(
    "/list/by/cell", response_model=ResponseCellModel, status_code=status.HTTP_200_OK
)
async def get_project_list_by_cell(
    cell_id: Union[int, None] = None,
    species_id: Union[int, None] = None,
    genes_positive: Union[str, None] = None,
    genes_negative: Union[str, None] = None,
    page: int = 0,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    filter_list = []
    if cell_id:
        filter_list.append(cellxgene.CellTypeMeta.id == cell_id)
    if species_id:
        filter_list.append(cellxgene.CellTypeMeta.species_id == species_id)
    if genes_positive:
        genes_positive_list = genes_positive.split(',')
        positive_filter_list = []
        for positive in genes_positive_list:
            positive_filter_list.append(cellxgene.CellTypeMeta.marker_gene_symbol.like("%{}%".format(positive)))
        filter_list.append(or_(*positive_filter_list))
    if genes_negative:
        genes_negative_list = genes_negative.split(',')
        negative_filter_list = []
        for negative in genes_negative_list:
            negative_filter_list.append(cellxgene.CellTypeMeta.marker_gene_symbol.notlike("%{}%".format(negative)))
        filter_list.append(and_(*negative_filter_list))
    cell_type_list = crud.get_project_by_cell(
        db=db, filters=filter_list, page=page, page_size=page_size
    )
    return ResponseMessage(status="0000", data=cell_type_list, message="ok")


@router.get(
    "/list/by/gene", response_model=ResponseGeneModel, status_code=status.HTTP_200_OK
)
async def get_project_list_by_gene(
    gene_symbol: Union[str, None] = None,
    species_id: Union[int, None] = None,
    page: int = 0,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    filter_list = []
    if gene_symbol:
        filter_list.append(cellxgene.GeneMeta.gene_symbol.like("%{}%".format(gene_symbol)))
    if species_id:
        filter_list.append(cellxgene.GeneMeta.species_id == species_id)
    gene_meta_list = crud.get_project_by_gene(
        db=db, filters=filter_list, page=page, page_size=page_size
    )
    return ResponseMessage(status="0000", data=gene_meta_list, message="ok")


@router.post("/upload", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def add_project(file: UploadFile = File()):
    content = await file.read()
    all_sheet_df = pd.read_excel(BytesIO(content), sheet_name=None, dtype=str)
    print(all_sheet_df.keys())
    return ResponseMessage(status="0000", data="ok", message="ok")


@router.post("/update", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def update_project(file: UploadFile = File()):
    content = await file.read()
    all_sheet_df = pd.read_excel(BytesIO(content), sheet_name=None, dtype=str)
    print(all_sheet_df.keys())
    return ResponseMessage(status="0000", data="ok", message="ok")


@router.get(
    "/species/list", response_model=ResponseMessage, status_code=status.HTTP_200_OK
)
async def get_species_list(db: Session = Depends(get_db)):
    species_list = crud.get_species_list(db=db, filters=None)
    return ResponseMessage(status="0000", data=species_list, message="ok")
