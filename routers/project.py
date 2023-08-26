from fastapi import (
    APIRouter,
    Depends,
    status,
    Header,
    Body,
    File,
    UploadFile,
    Request,
)
from orm.dependencies import get_db
from orm.schema.response import (
    ResponseMessage,
    ResponseProjectListModel,
    ResponseProjectDetailModel,
)
from orm import crud
from sqlalchemy.orm import Session
from orm.db_model import cellxgene
from utils import auth_util, mail_util
from conf import config
from typing import List, Union
from io import BytesIO
import pandas as pd
from sqlalchemy import and_, or_, distinct
from orm.dependencies import get_current_user
from orm.schema.project_model import TransferProjectModel
from fastapi.responses import RedirectResponse


router = APIRouter(
    prefix="/project",
    tags=["project"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/{project_id}",
    response_model=ResponseProjectDetailModel,
    status_code=status.HTTP_200_OK,
)
async def get_project_list(
    project_id: int,
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
) -> ResponseMessage:
    filter_list = [
        cellxgene.ProjectMeta.id == project_id,
        cellxgene.ProjectMeta.id == cellxgene.ProjectUser.project_id,
        cellxgene.ProjectUser.user_id == cellxgene.User.id,
        cellxgene.User.email_address == current_user_email_address,
    ]
    project_info_model = crud.get_project(db=db, filters=filter_list).first()
    if not project_info_model:
        return ResponseMessage(status="0201", data="无权限查看此项目", message="无权限查看此项目")
    return ResponseMessage(status="0000", data=project_info_model, message="ok")


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
    project_user_model = cellxgene.ProjectUser(user_id=owner)
    insert_project_model = cellxgene.ProjectMeta(
        title=title,
        description=description,
        status=new_project_status,
        tag=tag,
        owner=owner,
    )
    insert_project_model.project_project_user_meta.append(project_user_model)
    insert_analysis_model = cellxgene.Analysis()
    insert_analysis_model.analysis_project_meta = insert_project_model
    try:
        crud.create_analysis(db=db, insert_analysis_model=insert_analysis_model)
        return ResponseMessage(status="0000", data="项目创建成功", message="项目创建成功")
    except Exception as e:
        print(e)
        return ResponseMessage(status="0201", data="项目创建失败", message="项目创建失败")


@router.get("/organ/list", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def get_organ_list(
    organ: Union[str, None] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
):
    search_page = page - 1
    filter_list = []
    if organ:
        filter_list.append(cellxgene.BioSampleMeta.organ.like("%{}%".format(organ)))
    organ_list = crud.get_organ_list(db=db, filters=filter_list).distinct().offset(search_page).limit(page_size).all()
    return_organ_list = []
    for organ_info in organ_list:
        if organ_info.organ is not None:
            return_organ_list.append(organ_info.organ)
    return ResponseMessage(status="0000", data=return_organ_list, message="ok")


@router.get("/gene_symbol/list", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def get_gene_symbol_list(
    gene_symbol: Union[str, None] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
):
    search_page = page - 1
    filter_list = []
    if gene_symbol:
        filter_list.append(cellxgene.GeneMeta.gene_symbol.like("%{}%".format(gene_symbol)))
    gene_symbol_list = crud.get_gene_symbol_list(db=db, filters=filter_list).distinct().offset(search_page).limit(page_size).all()
    return_gene_symbol_list = []
    for return_gene_symbol_info in gene_symbol_list:
        if return_gene_symbol_info.gene_symbol is not None:
            return_gene_symbol_list.append(return_gene_symbol_info.gene_symbol)
    return ResponseMessage(status="0000", data=return_gene_symbol_list, message="ok")


@router.get(
    "/list/by/sample",
    response_model=ResponseProjectListModel,
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
    filter_list = [
        cellxgene.BioSampleMeta.id == cellxgene.ProjectBioSample.biosample_id,
        cellxgene.ProjectBioSample.project_id == cellxgene.ProjectUser.project_id,
        cellxgene.ProjectUser.user_id == cellxgene.User.id,
        cellxgene.User.email_address == current_user_email_address,
    ]
    if organ is not None:
        filter_list.append(cellxgene.BioSampleMeta.organ == organ)
    if species_id is not None:
        filter_list.append(cellxgene.BioSampleMeta.species_id == species_id)
    if external_sample_accesstion is not None:
        filter_list.append(
            cellxgene.BioSampleMeta.external_sample_accesstion
            == external_sample_accesstion
        )
    if disease is not None:
        filter_list.append(cellxgene.BioSampleMeta.disease.like("%{}%".format(disease)))
    if development_stage is not None:
        filter_list.append(
            cellxgene.BioSampleMeta.development_stage.like(
                "%{}%".format(development_stage)
            )
        )
    biosample_list = (
        crud.get_project_by_sample(db=db, filters=filter_list)
        .offset(search_page)
        .limit(page_size)
        .all()
    )
    total = crud.get_project_by_sample(db=db, filters=filter_list).count()
    res_dict = {
        "project_list": biosample_list,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    return ResponseMessage(status="0000", data=res_dict, message="ok")


@router.get(
    "/list/by/cell",
    response_model=ResponseProjectListModel,
    status_code=status.HTTP_200_OK,
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
    filter_list = [
        cellxgene.CellTypeMeta.id == cellxgene.CalcCellClusterProportion.cell_type_id,
        cellxgene.CalcCellClusterProportion.analysis_id == cellxgene.Analysis.id,
        cellxgene.Analysis.project_id == cellxgene.ProjectUser.project_id,
        cellxgene.ProjectUser.user_id == cellxgene.User.id,
        cellxgene.User.email_address == current_user_email_address,
    ]
    if cell_id is not None:
        filter_list.append(cellxgene.CellTypeMeta.id == cell_id)
    if species_id is not None:
        filter_list.append(cellxgene.CellTypeMeta.species_id == species_id)
    if genes_positive is not None:
        genes_positive_list = genes_positive.split(",")
        positive_filter_list = []
        for positive in genes_positive_list:
            positive_filter_list.append(
                cellxgene.CellTypeMeta.marker_gene_symbol.like("%{}%".format(positive))
            )
        filter_list.append(or_(*positive_filter_list))
    if genes_negative is not None:
        genes_negative_list = genes_negative.split(",")
        negative_filter_list = []
        for negative in genes_negative_list:
            negative_filter_list.append(
                cellxgene.CellTypeMeta.marker_gene_symbol.notlike(
                    "%{}%".format(negative)
                )
            )
        filter_list.append(and_(*negative_filter_list))
    cell_type_list = (
        crud.get_project_by_cell(db=db, filters=filter_list)
        .offset(search_page)
        .limit(page_size)
        .all()
    )
    total = crud.get_project_by_cell(db=db, filters=filter_list).count()
    res_dict = {
        "project_list": cell_type_list,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    return ResponseMessage(status="0000", data=res_dict, message="ok")


@router.get(
    "/list/by/gene",
    response_model=ResponseProjectListModel,
    status_code=status.HTTP_200_OK,
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
    filter_list = [
        cellxgene.GeneMeta.id == cellxgene.CellClusterGeneExpression.gene_id,
        cellxgene.CellClusterGeneExpression.calculated_cell_cluster_id
        == cellxgene.CalcCellClusterProportion.id,
        cellxgene.CalcCellClusterProportion.analysis_id == cellxgene.Analysis.id,
        cellxgene.Analysis.project_id == cellxgene.ProjectUser.project_id,
        cellxgene.ProjectUser.user_id == cellxgene.User.id,
        cellxgene.User.email_address == current_user_email_address,
    ]
    if gene_symbol is not None:
        filter_list.append(
            cellxgene.GeneMeta.gene_symbol.like("%{}%".format(gene_symbol))
        )
    if species_id is not None:
        filter_list.append(cellxgene.GeneMeta.species_id == species_id)
    gene_meta_list = (
        crud.get_project_by_gene(db=db, filters=filter_list)
        .offset(search_page)
        .limit(page_size)
        .all()
    )
    total = crud.get_project_by_gene(db=db, filters=filter_list).count()
    res_dict = {
        "project_list": gene_meta_list,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    return ResponseMessage(status="0000", data=res_dict, message="ok")


@router.post(
    "/{project_id}/transfer",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
)
async def transfer_project(
    project_id: int,
    transfer_to: TransferProjectModel = Body(),
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
):
    transfer_to_user_info = crud.get_user(
        db=db,
        filters=[cellxgene.User.email_address == transfer_to.transfer_to_email_address],
    ).first()
    if not transfer_to_user_info:
        return ResponseMessage(
            status="0201", data="转移对象的账号不存在，请确认邮箱是否正确", message="转移对象的账号不存在，请确认邮箱是否正确"
        )
    project_info = crud.get_project(
        db=db, filters=[cellxgene.ProjectMeta.id == project_id]
    ).first()
    if not project_info:
        return ResponseMessage(status="0201", data="项目不存在", message="项目不存在")
    if project_info.project_user_meta.email_address != current_user_email_address:
        return ResponseMessage(
            status="0201", data="您不是项目的拥有者，无法转移此项目", message="您不是项目的拥有者，无法转移此项目"
        )
    try:
        crud.update_project(
            db=db,
            filters=[cellxgene.ProjectMeta.id == project_id],
            update_dict={"owner": transfer_to_user_info.id},
        )
        return ResponseMessage(status="0000", data="项目转移成功", message="项目转移成功")
    except:
        return ResponseMessage(status="0201", data="项目转移失败", message="项目转移失败")


@router.post(
    "/file/upload", response_model=ResponseMessage, status_code=status.HTTP_200_OK
)
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


@router.get("/view/{h5ad_id}/{url_path:path}", status_code=status.HTTP_200_OK)
async def project_view_h5ad(
    h5ad_id: str,
    url_path: str,
    request_param: Request,
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
):
    filter_list = [
        cellxgene.Analysis.project_id == cellxgene.ProjectMeta.id,
        cellxgene.ProjectMeta.id == cellxgene.ProjectUser.project_id,
        cellxgene.ProjectUser.user_id == cellxgene.User.id,
        cellxgene.Analysis.h5ad_id == h5ad_id,
        cellxgene.User.email_address == current_user_email_address,
    ]
    analysis_info = crud.get_analysis(db=db, filters=filter_list).first()
    if analysis_info:
        return RedirectResponse("http://localhost:5005/view/{}/{}".format(h5ad_id, url_path) + "?" + str(request_param.query_params))
    else:
        return ResponseMessage(status="0201", data="无法查看此项目", message="无法查看此项目")
