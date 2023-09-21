from fastapi import (
    APIRouter,
    Depends,
    status,
    Body,
    File,
    Form,
    UploadFile,
    Request,
)
from orm.dependencies import get_db
from orm.schema.response import (
    ResponseMessage,
    ResponseProjectListModel,
    ResponseProjectDetailModel,
)
import json
import os
from orm import crud
from sqlalchemy.orm import Session
from orm.db_model import cellxgene
from conf import config
from typing import List, Union
from io import BytesIO
import pandas as pd
from sqlalchemy import and_, or_, distinct
from orm.dependencies import get_current_user
from orm.schema.project_model import TransferProjectModel
from fastapi.responses import RedirectResponse, FileResponse
from uuid import uuid4
from utils import file_util
from mqtt_consumer.consumer import SERVER_STATUS_DICT


PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


router = APIRouter(
    prefix="/project",
    tags=["project"],
    responses={404: {"description": "Not found"}},
)


@router.get("/homepage", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def get_view_homepage(db: Session = Depends(get_db)):
    species_list = (
        crud.get_species_list(
            db=db, query_list=[cellxgene.SpeciesMeta.species], filters=[]
        )
        .distinct(cellxgene.SpeciesMeta.species)
        .count()
    )
    sample_list = (
        crud.get_biosample(
            db=db, query_list=[cellxgene.BioSampleMeta.organ], filters=[]
        )
        .distinct()
        .count()
    )
    organ_list = (
        crud.get_biosample(
            db=db, query_list=[cellxgene.BioSampleMeta.biosample_type], filters=[]
        )
        .distinct()
        .count()
    )
    res_dict = {
        "species_list": species_list,
        "sample_list": sample_list,
        "organ_list": organ_list,
    }
    return ResponseMessage(status="0000", data=res_dict, message="ok")


@router.get(
    "/me", response_model=ResponseProjectDetailModel, status_code=status.HTTP_200_OK
)
async def get_user_project(
    title: Union[str, None] = None,
    is_publish: Union[int, None] = None,
    is_private: Union[int, None] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
) -> ResponseMessage:
    search_page = (page - 1) * page_size
    filter_list = [
        cellxgene.ProjectMeta.owner == cellxgene.User.id,
        cellxgene.User.email_address == current_user_email_address,
    ]
    if title is not None:
        filter_list.append(cellxgene.ProjectMeta.title.like("%{}%".format(title)))
    if is_publish is not None:
        filter_list.append(cellxgene.ProjectMeta.is_publish == is_publish)
    if is_private is not None:
        filter_list.append(cellxgene.ProjectMeta.is_private == is_private)
    project_list = (
        crud.get_project(db=db, filters=filter_list)
        .offset(search_page)
        .limit(page_size)
        .all()
    )
    total = crud.get_project(db, filters=filter_list).count()
    res_dict = {
        "project_list": project_list,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    return ResponseMessage(status="0000", data=res_dict, message="ok")


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
        return ResponseMessage(status="0201", data={}, message="无权限查看此项目")
    return ResponseMessage(status="0000", data=project_info_model, message="ok")


@router.get(
    "/analysis/{analysis_id}",
    response_model=ResponseProjectDetailModel,
    status_code=status.HTTP_200_OK,
)
async def get_analysis_list(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
) -> ResponseMessage:
    filter_list = [
        cellxgene.Analysis.id == analysis_id,
        cellxgene.Analysis.project_id == cellxgene.ProjectUser.project_id,
        cellxgene.ProjectUser.user_id == cellxgene.User.id,
        cellxgene.User.email_address == current_user_email_address,
    ]
    analysis_info_model = crud.get_analysis(db=db, filters=filter_list).first()
    if not analysis_info_model:
        return ResponseMessage(status="0201", data={}, message="无权限查看此项目")
    return ResponseMessage(status="0000", data=analysis_info_model, message="ok")


@router.post("/create", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def create_project(
    title: str = Body(),
    description: str = Body(),
    h5ad_id: str = Body(),
    tags: str = Body(),
    members: list = Body(),
    is_publish: int = Body(),
    is_private: int = Body(),
    species_id: int = Body(),
    organ: str = Body(),
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
) -> ResponseMessage:
    owner = (
        crud.get_user(db, [cellxgene.User.email_address == current_user_email_address])
        .first()
        .id
    )
    project_status = config.ProjectStatus.PROJECT_STATUS_DRAFT
    members.append(current_user_email_address)
    member_info_list = []
    if is_private:
        member_info_list = crud.get_user(
            db=db, filters=[cellxgene.User.email_address.in_(members)]
        ).all()
    if is_publish:
        if is_private:
            project_status = config.ProjectStatus.PROJECT_STATUS_AVAILABLE
        else:
            project_status = config.ProjectStatus.PROJECT_STATUS_NEED_AUDIT
    insert_project_model = cellxgene.ProjectMeta(
        title=title,
        description=description,
        is_publish=project_status,
        is_private=is_private,
        tags=tags,
        owner=owner,
    )
    for member_info in member_info_list:
        project_user_model = cellxgene.ProjectUser(user_id=member_info.id)
        insert_project_model.project_project_user_meta.append(project_user_model)
    # h5ad_id = str(uuid4()).replace("-", "")
    # h5ad_id = "pbmc3k.h5ad"
    insert_analysis_model = cellxgene.Analysis(h5ad_id=h5ad_id)
    insert_analysis_model.analysis_project_meta = insert_project_model
    insert_biosample_model = cellxgene.BioSampleMeta(species_id=species_id, organ=organ)
    biosample_id = crud.create_biosample(
        db=db, insert_biosample_model=insert_biosample_model
    )
    insert_project_model.project_project_biosample_meta.append(
        cellxgene.ProjectBioSample(biosample_id=biosample_id)
    )
    insert_analysis_model.analysis_biosample_analysis_meta.append(
        cellxgene.BioSampleAnalysis(biosample_id=biosample_id)
    )
    try:
        analysis_id, project_id = crud.create_analysis(
            db=db, insert_analysis_model=insert_analysis_model
        )
        crud.update_project(
            db=db,
            filters=[cellxgene.ProjectMeta.id == project_id],
            update_dict={"project_alias_id": "project" + str(project_id)},
        )
        return ResponseMessage(
            status="0000",
            data={"analysis_id": analysis_id, "project_id": project_id},
            message="项目创建成功",
        )
    except Exception as e:
        print(e)
        return ResponseMessage(status="0201", data={}, message="项目创建失败")


@router.post("/update", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def update_project(
    project_id: int = Body(),
    title: str = Body(),
    description: str = Body(),
    h5ad_id: str | None = Body(),
    tags: str = Body(),
    members: list = Body(),
    is_publish: int = Body(),
    is_private: int = Body(),
    species_id: int = Body(),
    organ: str = Body(),
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
) -> ResponseMessage:
    filter_list = [
        cellxgene.ProjectMeta.id == project_id,
        cellxgene.ProjectMeta.owner == cellxgene.User.id,
        cellxgene.User.email_address == current_user_email_address,
    ]
    project_info = crud.get_project(db=db, filters=filter_list).first()
    members.append(current_user_email_address)
    if not project_info:
        return ResponseMessage(status="0201", data={}, message="您无权更新此项目")
    if (project_info.is_publish == config.ProjectStatus.PROJECT_STATUS_DRAFT) or (
        project_info.is_publish == config.ProjectStatus.PROJECT_STATUS_AVAILABLE
        and is_publish == config.ProjectStatus.PROJECT_STATUS_AVAILABLE
        and project_info.is_private == config.ProjectStatus.PROJECT_STATUS_PRIVATE
    ):
        project_status = is_publish
        if (
            is_private == config.ProjectStatus.PROJECT_STATUS_PUBLIC
            and is_publish == config.ProjectStatus.PROJECT_STATUS_AVAILABLE
        ):
            project_status = config.ProjectStatus.PROJECT_STATUS_NEED_AUDIT
        update_project_dict = {
            "title": title,
            "description": description,
            "tags": tags,
            "is_publish": project_status,
            "is_private": is_private,
        }
        member_info_list = crud.get_user(
            db=db, filters=[cellxgene.User.email_address.in_(members)]
        ).all()
        insert_project_user_model_list = []
        for member_info in member_info_list:
            insert_project_user_model_list.append(
                cellxgene.ProjectUser(project_id=project_id, user_id=member_info.id)
            )
        update_biosample_id = project_info.project_project_biosample_meta[
            0
        ].biosample_id
        update_biosample_dict = {"species_id": species_id, "organ": organ}
        update_analysis_id = project_info.project_analysis_meta[0].id
        # h5ad_id = str(uuid4()).replace("-", "")
        update_analysis_dict = {"h5ad_id": h5ad_id}
        crud.project_update_transaction(
            db=db,
            delete_project_user_filters=[
                cellxgene.ProjectUser.project_id == project_id
            ],
            insert_project_user_model_list=insert_project_user_model_list,
            update_project_filters=[cellxgene.ProjectMeta.id == project_id],
            update_project_dict=update_project_dict,
            update_biosample_filters=[
                cellxgene.BioSampleMeta.id == update_biosample_id
            ],
            update_biosample_dict=update_biosample_dict,
            update_analysis_filters=[cellxgene.Analysis.id == update_analysis_id],
            update_analysis_dict=update_analysis_dict,
        )
    else:
        ResponseMessage(status="0000", data={}, message="更新状态异常")
    return ResponseMessage(status="0000", data={}, message="项目更新成功")


@router.post(
    "/{project_id}/offline",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
)
async def offline_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
):
    filter_list = [
        cellxgene.ProjectMeta.id == project_id,
        cellxgene.ProjectMeta.owner == cellxgene.User.id,
        cellxgene.User.email_address == current_user_email_address,
    ]
    project_info = crud.get_project(db=db, filters=filter_list).first()
    if not project_info:
        return ResponseMessage(status="0201", data={}, message="您无权下线此项目")
    if project_info.is_private == config.ProjectStatus.PROJECT_STATUS_PRIVATE:
        is_publish = config.ProjectStatus.PROJECT_STATUS_DRAFT
        try:
            crud.update_project(
                db=db,
                filters=[cellxgene.ProjectMeta.id == project_id],
                update_dict={"is_publish": is_publish},
            )
            return ResponseMessage(status="0000", data={}, message="项目下线成功")
        except:
            return ResponseMessage(status="0201", data={}, message="项目下线失败")
    else:
        return ResponseMessage(status="0201", data={}, message="您无权下线此项目")


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
        return ResponseMessage(status="0201", data={}, message="转移对象的账号不存在，请确认邮箱是否正确")
    project_info = crud.get_project(
        db=db, filters=[cellxgene.ProjectMeta.id == project_id]
    ).first()
    if not project_info:
        return ResponseMessage(status="0201", data={}, message="项目不存在")
    if project_info.project_user_meta.email_address != current_user_email_address:
        return ResponseMessage(status="0201", data={}, message="您不是项目的拥有者，无法转移此项目")
    if (
        project_info.is_private == config.ProjectStatus.PROJECT_STATUS_PRIVATE
        and project_info.is_publish != config.ProjectStatus.PROJECT_STATUS_UNAVAILABLE
    ):
        try:
            crud.update_project(
                db=db,
                filters=[cellxgene.ProjectMeta.id == project_id],
                update_dict={"owner": transfer_to_user_info.id},
            )
            return ResponseMessage(status="0000", data={}, message="项目转移成功")
        except:
            return ResponseMessage(status="0201", data={}, message="项目转移失败")
    else:
        return ResponseMessage(status="0201", data={}, message="当前状态不可转移项目")


@router.get(
    "/organ/list", response_model=ResponseMessage, status_code=status.HTTP_200_OK
)
async def get_organ_list(
    organ: Union[str, None] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
):
    search_page = (page - 1) * page_size
    filter_list = []
    if organ:
        filter_list.append(cellxgene.BioSampleMeta.organ.like("%{}%".format(organ)))
    organ_list = (
        crud.get_organ_list(db=db, filters=filter_list)
        .distinct()
        .offset(search_page)
        .limit(page_size)
        .all()
    )
    return_organ_list = []
    for organ_info in organ_list:
        if organ_info.organ is not None:
            return_organ_list.append(organ_info.organ)
    return ResponseMessage(status="0000", data=return_organ_list, message="ok")


@router.get(
    "/gene_symbol/list", response_model=ResponseMessage, status_code=status.HTTP_200_OK
)
async def get_gene_symbol_list(
    gene_symbol: Union[str, None] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
):
    search_page = (page - 1) * page_size
    filter_list = []
    if gene_symbol:
        filter_list.append(
            cellxgene.GeneMeta.gene_symbol.like("%{}%".format(gene_symbol))
        )
    gene_symbol_list = (
        crud.get_gene_symbol_list(db=db, filters=filter_list)
        .distinct()
        .offset(search_page)
        .limit(page_size)
        .all()
    )
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
    search_page = (page - 1) * page_size
    filter_list = [
        cellxgene.BioSampleMeta.id == cellxgene.ProjectBioSample.biosample_id,
        cellxgene.ProjectBioSample.project_id == cellxgene.ProjectUser.project_id,
        cellxgene.ProjectUser.user_id == cellxgene.User.id,
        cellxgene.User.email_address == current_user_email_address,
    ]
    public_filter_list = [
        cellxgene.BioSampleMeta.id == cellxgene.ProjectBioSample.biosample_id,
        cellxgene.ProjectBioSample.project_id == cellxgene.ProjectMeta.id,
        cellxgene.ProjectMeta.is_publish
        == config.ProjectStatus.PROJECT_STATUS_AVAILABLE,
        cellxgene.ProjectMeta.is_private == config.ProjectStatus.PROJECT_STATUS_PUBLIC,
    ]
    if organ is not None:
        filter_list.append(cellxgene.BioSampleMeta.organ == organ)
        public_filter_list.append(cellxgene.BioSampleMeta.organ == organ)
    if species_id is not None:
        filter_list.append(cellxgene.BioSampleMeta.species_id == species_id)
        public_filter_list.append(cellxgene.BioSampleMeta.species_id == species_id)
    if external_sample_accesstion is not None:
        filter_list.append(
            cellxgene.BioSampleMeta.external_sample_accesstion
            == external_sample_accesstion
        )
        public_filter_list.append(
            cellxgene.BioSampleMeta.external_sample_accesstion
            == external_sample_accesstion
        )
    if disease is not None:
        filter_list.append(cellxgene.BioSampleMeta.disease.like("%{}%".format(disease)))
        public_filter_list.append(
            cellxgene.BioSampleMeta.disease.like("%{}%".format(disease))
        )
    if development_stage is not None:
        filter_list.append(
            cellxgene.BioSampleMeta.development_stage.like(
                "%{}%".format(development_stage)
            )
        )
        public_filter_list.append(
            cellxgene.BioSampleMeta.development_stage.like(
                "%{}%".format(development_stage)
            )
        )
    biosample_list = (
        crud.get_project_by_sample(
            db=db, filters=filter_list, public_filter_list=public_filter_list
        )
        .distinct()
        .offset(search_page)
        .limit(page_size)
        .all()
    )
    total = (
        crud.get_project_by_sample(
            db=db, filters=filter_list, public_filter_list=public_filter_list
        )
        .distinct()
        .count()
    )
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
    search_page = (page - 1) * page_size
    filter_list = [
        cellxgene.CellTypeMeta.cell_type_id
        == cellxgene.CalcCellClusterProportion.cell_type_id,
        cellxgene.CalcCellClusterProportion.analysis_id == cellxgene.Analysis.id,
        cellxgene.Analysis.project_id == cellxgene.ProjectUser.project_id,
        cellxgene.ProjectUser.user_id == cellxgene.User.id,
        cellxgene.User.email_address == current_user_email_address,
    ]
    public_filter_list = [
        cellxgene.CellTypeMeta.cell_type_id
        == cellxgene.CalcCellClusterProportion.cell_type_id,
        cellxgene.CalcCellClusterProportion.analysis_id == cellxgene.Analysis.id,
        cellxgene.Analysis.project_id == cellxgene.ProjectMeta.id,
        cellxgene.ProjectMeta.is_publish
        == config.ProjectStatus.PROJECT_STATUS_AVAILABLE,
        cellxgene.ProjectMeta.is_private == config.ProjectStatus.PROJECT_STATUS_PUBLIC,
    ]
    if cell_id is not None:
        filter_list.append(cellxgene.CellTypeMeta.cell_type_id == cell_id)
        public_filter_list.append(cellxgene.CellTypeMeta.cell_type_id == cell_id)
    if species_id is not None:
        filter_list.append(cellxgene.CellTypeMeta.species_id == species_id)
        public_filter_list.append(cellxgene.CellTypeMeta.species_id == species_id)
    if genes_positive is not None:
        genes_positive_list = genes_positive.split(",")
        positive_filter_list = []
        for positive in genes_positive_list:
            positive_filter_list.append(
                cellxgene.CellTypeMeta.marker_gene_symbol.like("%{}%".format(positive))
            )
        filter_list.append(or_(*positive_filter_list))
        public_filter_list.append(or_(*positive_filter_list))
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
        public_filter_list.append(and_(*negative_filter_list))
    cell_type_list = (
        crud.get_project_by_cell(
            db=db, filters=filter_list, public_filter_list=public_filter_list
        )
        .distinct()
        .offset(search_page)
        .limit(page_size)
        .all()
    )
    total = (
        crud.get_project_by_cell(
            db=db, filters=filter_list, public_filter_list=public_filter_list
        )
        .distinct()
        .count()
    )
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
    search_page = (page - 1) * page_size
    filter_list = [
        cellxgene.GeneMeta.gene_ensemble_id
        == cellxgene.CellClusterGeneExpression.gene_ensemble_id,
        cellxgene.CellClusterGeneExpression.calculated_cell_cluster_id
        == cellxgene.CalcCellClusterProportion.calculated_cell_cluster_id,
        cellxgene.CalcCellClusterProportion.analysis_id == cellxgene.Analysis.id,
        cellxgene.Analysis.project_id == cellxgene.ProjectUser.project_id,
        cellxgene.ProjectUser.user_id == cellxgene.User.id,
        cellxgene.User.email_address == current_user_email_address,
    ]
    public_filter_list = [
        cellxgene.GeneMeta.gene_ensemble_id
        == cellxgene.CellClusterGeneExpression.gene_ensemble_id,
        cellxgene.CellClusterGeneExpression.calculated_cell_cluster_id
        == cellxgene.CalcCellClusterProportion.calculated_cell_cluster_id,
        cellxgene.CalcCellClusterProportion.analysis_id == cellxgene.Analysis.id,
        cellxgene.Analysis.project_id == cellxgene.ProjectMeta.id,
        cellxgene.ProjectMeta.is_publish
        == config.ProjectStatus.PROJECT_STATUS_AVAILABLE,
        cellxgene.ProjectMeta.is_private == config.ProjectStatus.PROJECT_STATUS_PUBLIC,
    ]
    if gene_symbol is not None:
        filter_list.append(
            cellxgene.GeneMeta.gene_symbol.like("%{}%".format(gene_symbol))
        )
        public_filter_list.append(
            cellxgene.GeneMeta.gene_symbol.like("%{}%".format(gene_symbol))
        )
    if species_id is not None:
        filter_list.append(cellxgene.GeneMeta.species_id == species_id)
        public_filter_list.append(cellxgene.GeneMeta.species_id == species_id)
    gene_meta_list = (
        crud.get_project_by_gene(
            db=db,
            query_list=[cellxgene.CellClusterGeneExpression],
            filters=filter_list,
            public_filter_list=public_filter_list,
        )
        .distinct()
        .offset(search_page)
        .limit(page_size)
        .all()
    )
    total = (
        crud.get_project_by_gene(
            db=db,
            query_list=[cellxgene.CellClusterGeneExpression],
            filters=filter_list,
            public_filter_list=public_filter_list,
        )
        .distinct()
        .count()
    )
    res_dict = {
        "project_list": gene_meta_list,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    return ResponseMessage(status="0000", data=res_dict, message="ok")


@router.get(
    "/list/by/gene/graph",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
)
async def get_project_list_by_gene(
    gene_symbol: Union[str, None] = None,
    species_id: Union[int, None] = None,
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
) -> ResponseMessage:
    filter_list = [
        cellxgene.GeneMeta.gene_ensemble_id
        == cellxgene.CellClusterGeneExpression.gene_ensemble_id,
        cellxgene.CellClusterGeneExpression.calculated_cell_cluster_id
        == cellxgene.CalcCellClusterProportion.calculated_cell_cluster_id,
        cellxgene.CalcCellClusterProportion.analysis_id == cellxgene.Analysis.id,
        cellxgene.Analysis.project_id == cellxgene.ProjectUser.project_id,
        cellxgene.ProjectUser.user_id == cellxgene.User.id,
        cellxgene.User.email_address == current_user_email_address,
    ]
    public_filter_list = [
        cellxgene.GeneMeta.gene_ensemble_id
        == cellxgene.CellClusterGeneExpression.gene_ensemble_id,
        cellxgene.CellClusterGeneExpression.calculated_cell_cluster_id
        == cellxgene.CalcCellClusterProportion.calculated_cell_cluster_id,
        cellxgene.CalcCellClusterProportion.analysis_id == cellxgene.Analysis.id,
        cellxgene.Analysis.project_id == cellxgene.ProjectMeta.id,
        cellxgene.ProjectMeta.is_publish
        == config.ProjectStatus.PROJECT_STATUS_AVAILABLE,
        cellxgene.ProjectMeta.is_private == config.ProjectStatus.PROJECT_STATUS_PUBLIC,
    ]
    if gene_symbol is not None:
        filter_list.append(
            cellxgene.GeneMeta.gene_symbol.like("%{}%".format(gene_symbol))
        )
        public_filter_list.append(
            cellxgene.GeneMeta.gene_symbol.like("%{}%".format(gene_symbol))
        )
    if species_id is not None:
        filter_list.append(cellxgene.GeneMeta.species_id == species_id)
        public_filter_list.append(cellxgene.GeneMeta.species_id == species_id)
    gene_meta_list = (
        crud.get_project_by_gene(
            db=db,
            query_list=[
                cellxgene.CellClusterGeneExpression.cell_proportion_expression_the_gene,
                cellxgene.CellClusterGeneExpression.average_gene_expression,
                cellxgene.CellTypeMeta.cell_type_name,
            ],
            filters=filter_list,
            public_filter_list=public_filter_list,
        )
        .distinct()
        .all()
    )
    res_list = []
    for gene_meta in gene_meta_list:
        res_list.append(
            {
                "cell_proportion_expression_the_gene": gene_meta.cell_proportion_expression_the_gene,
                "average_gene_expression": gene_meta.average_gene_expression,
                "cell_type_name": gene_meta.cell_type_name,
            }
        )
    return ResponseMessage(status="0000", data=res_list, message="ok")


@router.get("/{analysis_id}/graph/cell_number", response_model=ResponseProjectDetailModel, status_code=status.HTTP_200_OK)
async def view_cell_number_graph(
    analysis_id: int,
    db: Session = Depends(get_db),
    # current_user_email_address=Depends(get_current_user),
):
    cell_proportion_meta_list = crud.get_cell_proportion(db=db, filters=[cellxgene.CalcCellClusterProportion.analysis_id == analysis_id])
    return ResponseMessage(status="0000", data=cell_proportion_meta_list, message="ok")


@router.get("/{analysis_id}/graph/pathway", response_model=ResponseProjectDetailModel, status_code=status.HTTP_200_OK)
async def view_pathway_graph(
    analysis_id: int,
    db: Session = Depends(get_db),
    # current_user_email_address=Depends(get_current_user),
):
    pathway_meta_list = crud.get_pathway_score(db=db, filters=[cellxgene.PathwayScore.analysis_id == analysis_id])
    return ResponseMessage(status="0000", data=pathway_meta_list, message="ok")


@router.post(
    "/file/upload", response_model=ResponseMessage, status_code=status.HTTP_200_OK
)
async def upload_file(
    file: UploadFile = File(...),
    # chunknumber: str = Form(...),
    # identifier: str = Form(...),
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
) -> ResponseMessage:
    # if len(chunknumber) == 0 or len(identifier) == 0:
    #     return ResponseMessage(status="0201", data={}, message="没有传递相关参数")
    # task = identifier  # 获取文件唯一标识符
    # chunk = chunknumber  # 获取该分片在所有分片中的序号【客户端设定】
    # filename = '%s%s' % (task, chunk)  # 构成该分片唯一标识符
    current_user_info = crud.get_user(
        db=db, filters=[cellxgene.User.email_address == current_user_email_address]
    ).first()
    try:
        await file_util.save_file(db=db, file=file, insert_user_id=current_user_info.id)
    except:
        return ResponseMessage(status="0201", data={}, message="文件上传失败")
    else:
        return ResponseMessage(status="0000", data={}, message="文件上传成功")


@router.get(
    "/file/me",
    response_model=ResponseProjectListModel,
    status_code=status.HTTP_200_OK,
)
async def get_user_h5ad_file_list(
    file_name: Union[str, None] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
):
    search_page = (page - 1) * page_size
    filter_list = [
        cellxgene.User.email_address == current_user_email_address,
        cellxgene.FileLibrary.upload_user_id == cellxgene.User.id,
    ]
    if file_name:
        filter_list.append(
            cellxgene.FileLibrary.file_name.like("%{}%".format(file_name))
        )
    h5ad_file_list = (
        crud.get_h5ad(db=db, filters=filter_list)
        .offset(search_page)
        .limit(page_size)
        .all()
    )
    total = crud.get_h5ad(db=db, filters=filter_list).count()
    res_dict = {
        "h5ad_list": h5ad_file_list,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    return ResponseMessage(status="0000", data=res_dict, message="ok")


@router.get(
    "/species/list", response_model=ResponseMessage, status_code=status.HTTP_200_OK
)
async def get_species_list(
    db: Session = Depends(get_db), current_user_email_address=Depends(get_current_user)
) -> ResponseMessage:
    species_list = crud.get_species_list(
        db=db, query_list=[cellxgene.SpeciesMeta], filters=None
    ).all()
    return ResponseMessage(status="0000", data=species_list, message="ok")


@router.get(
    "/view/tree/cell_taxonomy",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
)
async def get_cell_taxonomy_tree(
    cell_marker: str,
    db: Session = Depends(get_db),
    # current_user_email_address = Depends(get_current_user),
):
    with open("./conf/celltype_relationship.json", "r", encoding="utf-8") as f:
        total_relation_list = json.load(f)
    filter_list = [
        cellxgene.CellTaxonomy.specific_cell_ontology_id
        == cellxgene.CellTaxonomyRelation.cl_id,
        cellxgene.CellTaxonomy.cell_marker == cell_marker,
    ]
    cell_taxonomy_relation_model_list = crud.get_cell_taxonomy_relation(
        db=db, query_list=[cellxgene.CellTaxonomyRelation], filters=filter_list
    ).all()
    res = []
    for cell_taxonomy_relation_model in cell_taxonomy_relation_model_list:
        # relation_dict = {"cl_id": cell_taxonomy_relation_model.cl_id}
        parent_dict = get_parent_id(
            total_relation_list, cell_taxonomy_relation_model.cl_id, {}
        )
        # relation_dict["parent_dict"] = parent_dict
        res.append(parent_dict)
    return ResponseMessage(status="0000", data=res, message="ok")


@router.get("/view/file/{file_id}", status_code=status.HTTP_200_OK)
async def get_csv_data(
    file_id: str,
    # current_user_email_address=Depends(get_current_user),
):
    file_path = PROJECT_ROOT + "/" + config.H5AD_FILE_PATH + "/" + file_id
    print(file_path)
    try:
        return FileResponse(
            file_path,
            media_type="application/octet-stream",
            filename=file_id,
        )
    except:
        return ResponseMessage(status="0201", data={}, message="文件不存在")


@router.get("/view/{analysis_id}/{url_path:path}", status_code=status.HTTP_200_OK)
async def project_view_h5ad(
    analysis_id: int,
    url_path: str,
    request_param: Request,
    db: Session = Depends(get_db),
    # current_user_email_address=Depends(get_current_user),
):
    filter_list = [
        cellxgene.Analysis.id
        == analysis_id
        # cellxgene.Analysis.project_id == cellxgene.ProjectMeta.id,
        # cellxgene.ProjectMeta.id == cellxgene.ProjectUser.project_id,
        # cellxgene.ProjectUser.user_id == cellxgene.User.id,
        # cellxgene.Analysis.h5ad_id == h5ad_id,
        # cellxgene.User.email_address == current_user_email_address,
    ]
    analysis_info = crud.get_analysis(db=db, filters=filter_list).first()
    if analysis_info:
        return RedirectResponse(
            config.CELLXGENE_GATEWAY_URL
            + "/view/"
            + "{}/{}".format(analysis_info.h5ad_id, url_path)
            + "?"
            + str(request_param.query_params)
        )
    else:
        return ResponseMessage(status="0201", data={}, message="无法查看此项目")


def get_parent_id(relation_list, cl_id, parent_dict):
    for i in relation_list:
        if i.get("id") == cl_id:
            parent_dict['cl_id'] = i.get("id")
            parent_dict['parent_dict'] = {}
            get_parent_id(relation_list, i.get("pId"), parent_dict['parent_dict'])
        if i.get("id") == "CL:0000000":
            return parent_dict
