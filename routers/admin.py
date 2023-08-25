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
from fastapi.responses import RedirectResponse
from orm.schema import project_model, user_model
from orm.schema.response import (
    ResponseMessage,
    ResponseUserModel,
    ResponseProjectDetailModel,
    ResponseProjectListModel,
)
from orm import crud
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from orm.db_model import cellxgene
from utils import auth_util, mail_util
from conf import config
from typing import List, Union
from io import BytesIO
import pandas as pd
from orm.dependencies import get_db, get_current_admin

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/user/list", response_model=ResponseUserModel, status_code=status.HTTP_200_OK
)
async def get_user_list(
    email_address: Union[str, None] = None,
    user_name: Union[str, None] = None,
    organization: Union[str, None] = None,
    state: Union[int, None] = None,
    create_at: Union[str, None] = None,
    page: int = 1,
    page_size: int = 20,
    asc: int = 1,
    db: Session = Depends(get_db),
    current_admin_email_address=Depends(get_current_admin),
) -> ResponseMessage:
    filter_list = []
    search_page = page - 1
    if email_address is not None:
        filter_list.append(
            cellxgene.User.email_address.like("%{}%".format(email_address))
        )
    if user_name is not None:
        filter_list.append(cellxgene.User.user_name.like("%{}%".format(user_name)))
    if organization is not None:
        filter_list.append(
            cellxgene.User.organization.like("%{}%".format(organization))
        )
    if state is not None:
        filter_list.append(cellxgene.User.state == state)
    if create_at is not None:
        filter_list.append(cellxgene.User.create_at.like("%{}%".format(create_at)))
    if asc is not None:
        user_model_list = (
            crud.get_user(db, filters=filter_list)
            .order_by(cellxgene.User.id.asc())
            .offset(search_page)
            .limit(page_size)
            .all()
        )
    else:
        user_model_list = (
            crud.get_user(db, filters=filter_list)
            .order_by(cellxgene.User.id.desc())
            .offset(search_page)
            .limit(page_size)
            .all()
        )
    total = crud.get_user(db, filters=filter_list).count()
    res_dict = {
        "user_list": user_model_list,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    return ResponseMessage(status="0000", data=res_dict, message="success")


@router.get(
    "/user/{user_id}", response_model=ResponseUserModel, status_code=status.HTTP_200_OK
)
async def get_user_info(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin_email_address: str = Depends(get_current_admin),
) -> ResponseMessage:
    search_user_info_model = crud.get_user(db, [cellxgene.User.id == user_id]).first()
    if search_user_info_model:
        return ResponseMessage(
            status="0000", data=search_user_info_model, message="success"
        )
    else:
        return ResponseMessage(status="0201", data="用户不存在", message="用户不存在")


@router.post(
    "/user/{user_id}/edit",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
)
async def edit_user_info(
    user_id: int,
    user_info: user_model.AdminEditInfoUserModel = Body(),
    db: Session = Depends(get_db),
    current_admin_email_address=Depends(get_current_admin),
) -> ResponseMessage:
    if not user_info:
        return ResponseMessage(status="0201", data="无更新内容", message="无更新内容")
    if user_info.email_address:
        check_user_model = crud.get_user(
            db, [cellxgene.User.email_address == user_info.email_address]
        ).first()
        if check_user_model:
            return ResponseMessage(status="0201", data="此邮箱已有账号", message="此邮箱已有账号")
    update_user_dict = {}
    for key, value in user_info.to_dict().items():
        if value:
            update_user_dict[key] = value
    if user_info.user_password:
        salt, jwt_user_password = auth_util.create_md5_password(
            salt=None, password=user_info.user_password
        )
        update_user_dict["user_password"] = jwt_user_password
        update_user_dict["salt"] = salt
    crud.update_user(
        db,
        [cellxgene.User.id == user_id],
        update_user_dict,
    )
    return ResponseMessage(status="0000", data="用户信息更新成功", message="用户信息更新成功")


@router.get(
    "/project/list",
    response_model=ResponseProjectDetailModel,
    status_code=status.HTTP_200_OK,
)
async def get_project_list(
    status: Union[str, None] = None,
    create_at: Union[str, None] = None,
    page: int = 1,
    page_size: int = 20,
    asc: int = 1,
    db: Session = Depends(get_db),
    current_admin_email_address=Depends(get_current_admin),
) -> ResponseMessage:
    search_page = page - 1
    filter_list = []
    if status is not None:
        filter_list.append(cellxgene.ProjectMeta.status == status)
    if asc:
        project_info_model_list = (
            crud.get_project(db=db, filters=filter_list)
            .order_by(cellxgene.ProjectMeta.id.asc())
            .offset(search_page)
            .limit(page_size)
            .all()
        )
    else:
        project_info_model_list = (
            crud.get_project(db=db, filters=filter_list)
            .order_by(cellxgene.ProjectMeta.id.desc())
            .offset(search_page)
            .limit(page_size)
            .all()
        )
    total = crud.get_project(db, filters=filter_list).count()
    res_dict = {
        "project_list": project_info_model_list,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    return ResponseMessage(status="0000", data=res_dict, message="ok")


@router.get(
    "/project/{project_id}",
    response_model=ResponseProjectDetailModel,
    status_code=status.HTTP_200_OK,
)
async def get_project_list(
    project_id: int,
    db: Session = Depends(get_db),
    current_admin_email_address=Depends(get_current_admin),
) -> ResponseMessage:
    filter_list = [
        cellxgene.ProjectMeta.id == project_id,
    ]
    project_info_model = crud.get_project(db=db, filters=filter_list).first()
    if not project_info_model:
        return ResponseMessage(status="0201", data="无此项目", message="无此项目")
    return ResponseMessage(status="0000", data=project_info_model, message="ok")


@router.post(
    "/project/{project_id}/status/update",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
)
async def update_project(
    project_id: int,
    project_status: project_model.UpdateProjectModel = Body(),
    db: Session = Depends(get_db),
    current_admin_email_address=Depends(get_current_admin),
):
    try:
        crud.update_project(
            db=db,
            filters=[cellxgene.ProjectMeta.id == project_id],
            update_dict={"status": project_status},
        )
        return ResponseMessage(status="0000", data="项目状态更新成功", message="项目状态更新成功")
    except:
        return ResponseMessage(status="0201", data="项目状态更新失败", message="项目状态更新失败")


@router.get(
    "/project/cell/list",
    response_model=ResponseProjectListModel,
    status_code=status.HTTP_200_OK,
)
async def get_cell_list(
    cell_id: Union[int, None] = None,
    species_id: Union[int, None] = None,
    genes_positive: Union[str, None] = None,
    genes_negative: Union[str, None] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_admin_email_address=Depends(get_current_admin),
):
    filter_list = []
    search_page = page - 1
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
        "cell_type_list": cell_type_list,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    return ResponseMessage(status="0000", data=res_dict, message="ok")


@router.get(
    "/project/gene/list",
    response_model=ResponseProjectListModel,
    status_code=status.HTTP_200_OK,
)
async def get_project_list_by_gene(
    gene_symbol: Union[str, None] = None,
    species_id: Union[int, None] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_admin_email_address=Depends(get_current_admin),
) -> ResponseMessage:
    search_page = page - 1
    filter_list = []
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
        "gene_meta_list": gene_meta_list,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    return ResponseMessage(status="0000", data=res_dict, message="ok")


@router.get("/project/process/cache_status", status_code=status.HTTP_200_OK)
async def get_project_cache_status(
    current_admin_email_address=Depends(get_current_admin),
):
    return RedirectResponse("http://localhost:5005/cache_status")


@router.get("/project/process/{h5ad_id}/terminate", status_code=status.HTTP_200_OK)
async def terminate_project_process(
    h5ad_id: str,
    current_admin_email_address=Depends(get_current_admin),
):
    return RedirectResponse("http://localhost:5005/terminate/{}".format(h5ad_id) + "?source_name=local")
