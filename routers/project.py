from fastapi import (
    APIRouter,
    Depends,
    status,
    Header,
    Body,
    File,
    UploadFile,
)
from orm.dependencies import get_db
from orm.schema.response import (
    ResponseMessage, ResponseProjectModel
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
from orm.dependencies import get_current_user


router = APIRouter(
    prefix="/project",
    tags=["project"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/list/{project_id}", response_model=ResponseMessage, status_code=status.HTTP_200_OK
)
async def get_project_list(
    project_id: int,
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
) -> ResponseMessage:
    project_info_model = crud.get_project_detail(db=db, project_id=project_id)
    if not project_info_model:
        return ResponseMessage(status="0201", data="无此项目", message="无此项目")
    return ResponseMessage(
        status="0000", data=project_info_model.to_dict(), message="ok"
    )


@router.post("/create", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def create_project(
    title: str = Body(),
    description: str = Body(),
    # h5ad_file: UploadFile | None = Body(),
    tag: str = Body(),
    project_status: str = Body(),
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
) -> ResponseMessage:
    owner = (
        crud.get_user(db, [cellxgene.User.email_address == current_user_email_address])
        .first()
        .id
    )
    new_project_status = config.ProjectStatus.INSERT_MAPPING_PROJECT_STATUS_DICT.get(
        project_status
    )
    insert_project_model = cellxgene.ProjectMeta(
        title=title,
        description=description,
        status=new_project_status,
        tag=tag,
        owner=owner,
    )
    insert_analysis_model = cellxgene.Analysis()
    insert_analysis_model.analysis_project_meta = insert_project_model
    try:
        crud.create_analysis(db=db, insert_analysis_model=insert_analysis_model)
        return ResponseMessage(status="0000", data="项目创建成功", message="项目创建成功")
    except:
        return ResponseMessage(status="0201", data="项目创建失败", message="项目创建失败")


@router.get(
    "/list/by/sample",
    response_model=ResponseProjectModel,
    status_code=status.HTTP_200_OK,
)
async def get_project_list_by_sample(
    organ: Union[str, None] = None,
    species_id: Union[int, None] = None,
    external_sample_accesstion: Union[str, None] = None,
    disease: Union[str, None] = None,
    development_stage: Union[str, None] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
) -> ResponseMessage:
    search_page = page - 1
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
        db=db, filters=filter_list
    ).offset(search_page).limit(page_size).all()
    total = crud.get_project_by_sample(
        db=db, filters=filter_list
    ).count()
    res_dict = {
        "project_list": biosample_list,
        "total": total,
        "page": page,
        "page_size": page_size
    }
    return ResponseMessage(status="0000", data=res_dict, message="ok")


@router.get(
    "/list/by/cell", response_model=ResponseProjectModel, status_code=status.HTTP_200_OK
)
async def get_project_list_by_cell(
    cell_id: Union[int, None] = None,
    species_id: Union[int, None] = None,
    genes_positive: Union[str, None] = None,
    genes_negative: Union[str, None] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
) -> ResponseMessage:
    search_page = page - 1
    filter_list = []
    if cell_id:
        filter_list.append(cellxgene.CellTypeMeta.id == cell_id)
    if species_id:
        filter_list.append(cellxgene.CellTypeMeta.species_id == species_id)
    if genes_positive:
        genes_positive_list = genes_positive.split(",")
        positive_filter_list = []
        for positive in genes_positive_list:
            positive_filter_list.append(
                cellxgene.CellTypeMeta.marker_gene_symbol.like("%{}%".format(positive))
            )
        filter_list.append(or_(*positive_filter_list))
    if genes_negative:
        genes_negative_list = genes_negative.split(",")
        negative_filter_list = []
        for negative in genes_negative_list:
            negative_filter_list.append(
                cellxgene.CellTypeMeta.marker_gene_symbol.notlike(
                    "%{}%".format(negative)
                )
            )
        filter_list.append(and_(*negative_filter_list))
    cell_type_list = crud.get_project_by_cell(
        db=db, filters=filter_list
    ).offset(search_page).limit(page_size).all()
    total = crud.get_project_by_cell(
        db=db, filters=filter_list
    ).count()
    res_dict = {
        "project_list": cell_type_list,
        "total": total,
        "page": page,
        "page_size": page_size
    }
    return ResponseMessage(status="0000", data=res_dict, message="ok")


@router.get(
    "/list/by/gene", response_model=ResponseProjectModel, status_code=status.HTTP_200_OK
)
async def get_project_list_by_gene(
    gene_symbol: Union[str, None] = None,
    species_id: Union[int, None] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
) -> ResponseMessage:
    search_page = page - 1
    filter_list = []
    if gene_symbol:
        filter_list.append(
            cellxgene.GeneMeta.gene_symbol.like("%{}%".format(gene_symbol))
        )
    if species_id:
        filter_list.append(cellxgene.GeneMeta.species_id == species_id)
    gene_meta_list = crud.get_project_by_gene(
        db=db, filters=filter_list
    ).offset(search_page).limit(page_size).all()
    total = crud.get_project_by_gene(
        db=db, filters=filter_list
    ).count()
    res_dict = {
        "project_list": gene_meta_list,
        "total": total,
        "page": page,
        "page_size": page_size
    }
    return ResponseMessage(status="0000", data=res_dict, message="ok")


@router.post("/upload", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def add_project(
    file: UploadFile = File(), current_user_email_address=Depends(get_current_user)
) -> ResponseMessage:
    content = await file.read()
    all_sheet_df = pd.read_excel(BytesIO(content), sheet_name=None, dtype=str)
    print(all_sheet_df.keys())
    return ResponseMessage(status="0000", data="ok", message="ok")


@router.post("/update", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def update_project(
    file: UploadFile = File(), current_user_email_address=Depends(get_current_user)
) -> ResponseMessage:
    content = await file.read()
    all_sheet_df = pd.read_excel(BytesIO(content), sheet_name=None, dtype=str)
    print(all_sheet_df.keys())
    return ResponseMessage(status="0000", data="ok", message="ok")


@router.get(
    "/species/list", response_model=ResponseMessage, status_code=status.HTTP_200_OK
)
async def get_species_list(
    db: Session = Depends(get_db), current_user_email_address=Depends(get_current_user)
) -> ResponseMessage:
    species_list = crud.get_species_list(db=db, filters=None)
    return ResponseMessage(status="0000", data=species_list, message="ok")
