import logging
import time
from datetime import datetime
import shutil
import xlsxwriter
from fastapi import (
    APIRouter,
    Depends,
    status,
    Body,
    File,
    Form,
    UploadFile,
    Request,
    Header,
)
from orm.dependencies import get_db
from orm.schema.response import (
    ResponseMessage,
    ResponseProjectListModel,
    ResponseProjectDetailModel,
)
import json
import os
import plotly.express as px
from io import BytesIO
from orm import crud
from sqlalchemy.orm import Session
from orm.db_model import cellxgene
from conf import config, table_config
from typing import List, Union, Annotated
import pandas as pd
from sqlalchemy import and_, or_, distinct, func
from orm.dependencies import get_current_user
from orm.schema.project_model import (
    TransferProjectModel,
    CopyToProjectModel,
    ProjectCreateModel,
    ProjectUpdateModel,
    ProjectModel,
)
from fastapi.responses import (
    RedirectResponse,
    FileResponse,
    Response,
    StreamingResponse,
)
from uuid import uuid4
from utils import file_util, auth_util, dict_util, cell_number_util, check_file_name_util
from mqtt_consumer.consumer import SERVER_STATUS_DICT
from orm.database import cellxgene_engine

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

router = APIRouter(
    prefix="/project",
    tags=["project"],
    responses={200: {"description": {"status": "0000", "data": {}, "message": "failed"}}},
)


@router.get("/homepage", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def get_view_homepage(db: Session = Depends(get_db)):
    species_list = (
        crud.get_species_list(
            db=db,
            query_list=[
                cellxgene.SpeciesMeta.id,
                cellxgene.SpeciesMeta.species,
                cellxgene.SpeciesMeta.species_ontology_label,
                func.count(distinct(cellxgene.ProjectMeta.id)),
            ],
            filters=[
                cellxgene.ProjectMeta.id == cellxgene.ProjectBioSample.project_id,
                cellxgene.ProjectBioSample.biosample_id == cellxgene.BioSampleMeta.id,
                cellxgene.SpeciesMeta.id == cellxgene.BioSampleMeta.species_id,
                cellxgene.ProjectMeta.is_publish
                == config.ProjectStatus.PROJECT_STATUS_IS_PUBLISH,
                cellxgene.ProjectMeta.is_private
                == config.ProjectStatus.PROJECT_STATUS_PUBLIC,
            ],
        )
        .distinct()
        .group_by(cellxgene.SpeciesMeta.id)
        .all()
    )
    # sample_list = (
    #     crud.get_biosample(
    #         db=db,
    #         query_list=[
    #             cellxgene.BioSampleMeta.biosample_type,
    #             func.count(cellxgene.ProjectMeta.id),
    #         ],
    #         filters=[cellxgene.ProjectMeta.id == cellxgene.ProjectBioSample.project_id,
    #                  cellxgene.ProjectBioSample.biosample_id == cellxgene.BioSampleMeta.id,
    #                  cellxgene.ProjectMeta.is_publish
    #                  == config.ProjectStatus.PROJECT_STATUS_IS_PUBLISH,
    #                  cellxgene.ProjectMeta.is_private == config.ProjectStatus.PROJECT_STATUS_PUBLIC,
    #                  ],
    #     )
    #     .group_by(cellxgene.BioSampleMeta.biosample_type)
    #     .all()
    # )
    organ_list = (
        crud.get_biosample(
            db=db,
            query_list=[
                cellxgene.BioSampleMeta.organ,
                func.count(distinct(cellxgene.ProjectMeta.id)),
            ],
            filters=[
                cellxgene.ProjectMeta.id == cellxgene.ProjectBioSample.project_id,
                cellxgene.ProjectBioSample.biosample_id == cellxgene.BioSampleMeta.id,
                cellxgene.ProjectMeta.is_publish
                == config.ProjectStatus.PROJECT_STATUS_IS_PUBLISH,
                cellxgene.ProjectMeta.is_private
                == config.ProjectStatus.PROJECT_STATUS_PUBLIC,
            ],
        )
        .group_by(cellxgene.BioSampleMeta.organ)
        .all()
    )
    project_meta_list = (
        crud.get_project(
            db=db,
            filters=[
                cellxgene.ProjectMeta.is_private
                == config.ProjectStatus.PROJECT_STATUS_PUBLIC,
                cellxgene.ProjectMeta.is_publish
                == config.ProjectStatus.PROJECT_STATUS_IS_PUBLISH,
            ],
        )
        .order_by(cellxgene.ProjectMeta.id.desc())
        .limit(config.ProjectStatus.HOMEPAGE_SHOW_PROJECT_LIMIT)
        .all()
    )
    return_species_list, return_biosample_type_list, return_organ_list = [], [], []
    for species_meta in species_list:
        return_species_list.append(
            {
                "species": species_meta[1],
                "species_label": species_meta[2],
                "count": species_meta[3],
                "id": species_meta[0],
            }
        )
    # for biosample_type_meta in sample_list:
    #     return_biosample_type_list.append(
    #         {"biosample_type": biosample_type_meta[0], "count": biosample_type_meta[1]}
    #     )
    for organ_meta in organ_list:
        return_organ_list.append({"organ": organ_meta[0], "count": organ_meta[1]})
    project_count = crud.get_project(
        db=db,
        filters=[
            cellxgene.ProjectMeta.is_publish
            == config.ProjectStatus.PROJECT_STATUS_IS_PUBLISH,
            cellxgene.ProjectMeta.is_private
            == config.ProjectStatus.PROJECT_STATUS_PUBLIC,
        ],
    ).count()
    sample_count = (
        crud.get_biosample(
            db=db,
            query_list=[func.sum(cellxgene.ProjectMeta.biosample_number)],
            filters=[
                cellxgene.ProjectMeta.is_publish
                == config.ProjectStatus.PROJECT_STATUS_IS_PUBLISH,
                cellxgene.ProjectMeta.is_private
                == config.ProjectStatus.PROJECT_STATUS_PUBLIC,
            ],
        )
        .distinct()
        .first()
    )[0]
    cell_type_count = (
        crud.get_project_by_cell_join(
            db=db,
            query_list=[cellxgene.CalcCellClusterProportion.cell_type_id],
            public_filter_list=[
                cellxgene.ProjectMeta.is_publish
                == config.ProjectStatus.PROJECT_STATUS_IS_PUBLISH,
                cellxgene.ProjectMeta.is_private
                == config.ProjectStatus.PROJECT_STATUS_PUBLIC,
                cellxgene.ProjectMeta.id == cellxgene.Analysis.project_id,
                cellxgene.CalcCellClusterProportion.analysis_id
                == cellxgene.Analysis.id,
            ],
        )
        .distinct()
        .count()
    )
    cell_number_list = (
        crud.get_project_by_cell_join(
            db=db,
            query_list=[cellxgene.CalcCellClusterProportion],
            public_filter_list=[
                cellxgene.ProjectMeta.is_publish
                == config.ProjectStatus.PROJECT_STATUS_IS_PUBLISH,
                cellxgene.ProjectMeta.is_private
                == config.ProjectStatus.PROJECT_STATUS_PUBLIC,
                cellxgene.ProjectMeta.id == cellxgene.Analysis.project_id,
                cellxgene.CalcCellClusterProportion.analysis_id
                == cellxgene.Analysis.id,
            ],
        )
        .distinct()
        .all()
    )
    cell_number_count = 0
    for cell_number_meta in cell_number_list:
        cell_number_count += cell_number_meta.cell_number
    statical_list = [
        {"statical": "project", "count": project_count},
        {"statical": "sample", "count": sample_count},
        {"statical": "cell_type", "count": cell_type_count},
        {"statical": "cell", "count": cell_number_count},
    ]
    res_dict = {
        "species_list": return_species_list,
        # "sample_list": return_biosample_type_list,
        "organ_list": return_organ_list,
        "project_list": [project_meta.to_dict() for project_meta in project_meta_list],
        "statical_list": statical_list,
    }
    return ResponseMessage(status="0000", data=res_dict, message="ok")


@router.get(
    "/me", response_model=ResponseProjectDetailModel, status_code=status.HTTP_200_OK
)
async def get_user_project(
    title: Union[str, None] = None,
    is_publish: Union[int, None] = None,
    is_private: Union[int, None] = None,
    tag: Union[str, None] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
) -> ResponseMessage:
    search_page = (page - 1) * page_size
    filter_list = [
        cellxgene.ProjectMeta.id == cellxgene.ProjectUser.project_id,
        cellxgene.ProjectUser.user_id == cellxgene.User.id,
        cellxgene.User.email_address == current_user_email_address,
        cellxgene.ProjectMeta.is_private == config.ProjectStatus.PROJECT_STATUS_PRIVATE,
        cellxgene.ProjectMeta.is_publish != config.ProjectStatus.PROJECT_STATUS_DELETE
    ]
    if title is not None:
        filter_list.append(cellxgene.ProjectMeta.title.like("%{}%".format(title)))
    if is_publish is not None:
        filter_list.append(cellxgene.ProjectMeta.is_publish == is_publish)
    if is_private is not None:
        filter_list.append(cellxgene.ProjectMeta.is_private == is_private)
    if tag is not None:
        filter_list.append(cellxgene.ProjectMeta.tags.like("%{}%".format(tag)))
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
    "/me/memory_cost",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK
)
async def get_user_memory_cost(
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
):
    owner = (
        crud.get_user(db, [cellxgene.User.email_address == current_user_email_address])
        .first()
        .id
    )
    file_size_meta = crud.get_file_info(db=db,
                                        query_list=[func.sum(cellxgene.FileLibrary.file_size)],
                                        filters=[cellxgene.FileLibrary.upload_user_id == owner,
                                                 cellxgene.FileLibrary.file_status == config.FileStatus.NORMAL]
                                        ).first()
    project_count = crud.get_project(db=db,
                                     filters=[cellxgene.ProjectMeta.owner == owner,
                                              cellxgene.ProjectMeta.is_publish != config.ProjectStatus.PROJECT_STATUS_DELETE]
                                     ).count()
    if not file_size_meta[0]:
        whole_file_size = 0
    else:
        whole_file_size = file_size_meta[0]
    return ResponseMessage(status="0000", data={"disk_space": whole_file_size, "project_count": project_count}, message="ok")


@router.get(
    "/{project_id}",
    response_model=ResponseProjectDetailModel,
    status_code=status.HTTP_200_OK,
)
async def get_project_info(
    project_id: int,
    db: Session = Depends(get_db),
    Authorization: Annotated[str | None, Header()] = None,
) -> ResponseMessage:
    filter_list = [
        cellxgene.ProjectMeta.id == project_id,
        cellxgene.ProjectMeta.is_publish != config.ProjectStatus.PROJECT_STATUS_DELETE
    ]
    project_info_model = crud.get_project(db=db, filters=filter_list).first()
    if not project_info_model:
        return ResponseMessage(status="0201", data={}, message="Project does not exist")
    if project_info_model.is_publish and not project_info_model.is_private:
        return ResponseMessage(status="0000", data=project_info_model, message="ok")
    elif project_info_model.is_private:
        if Authorization:
            current_user_email_address = await get_current_user(
                token=Authorization.split()[1]
            )
            private_filter_list = [
                cellxgene.ProjectMeta.id == project_id,
                cellxgene.ProjectMeta.id == cellxgene.ProjectUser.project_id,
                cellxgene.ProjectUser.user_id == cellxgene.User.id,
                cellxgene.User.email_address == current_user_email_address,
            ]
            private_project_info_model = crud.get_project(
                db=db, filters=private_filter_list
            ).first()
            if private_project_info_model:
                return ResponseMessage(
                    status="0000", data=private_project_info_model, message="ok"
                )
            else:
                return ResponseMessage(status="0201", data={}, message="permission denied")
        else:
            return ResponseMessage(status="0201", data={}, message="permission denied")
    else:
        return ResponseMessage(status="0201", data={}, message="permission denied")


@router.delete(
    "/{project_id}",
    response_model=ResponseProjectDetailModel,
    status_code=status.HTTP_200_OK,
)
async def get_project_info(
    project_id: int,
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
) -> ResponseMessage:
    filter_list = [
        cellxgene.ProjectMeta.id == project_id,
        cellxgene.ProjectMeta.owner == cellxgene.User.id,
        cellxgene.User.email_address == current_user_email_address,
    ]
    project_info = crud.get_project(db=db, filters=filter_list).first()
    if not project_info:
        return ResponseMessage(status="0201", data={}, message="permission denied")
    crud.update_project(db=db,
                        filters=[cellxgene.ProjectMeta.id == project_id],
                        update_dict={"is_publish": config.ProjectStatus.PROJECT_STATUS_DELETE})
    return ResponseMessage(status="0000", data={}, message="项目删除成功")


@router.get(
    "/analysis/{analysis_id}",
    response_model=ResponseProjectDetailModel,
    status_code=status.HTTP_200_OK,
)
async def get_analysis_detail(
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
        return ResponseMessage(status="0201", data={}, message="permission denied")
    return ResponseMessage(status="0000", data=analysis_info_model, message="ok")


@router.post("/create", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def create_project(
    create_project_model: ProjectCreateModel,
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
) -> ResponseMessage:
    owner = (
        crud.get_user(db, [cellxgene.User.email_address == current_user_email_address])
        .first()
        .id
    )
    already_exist_project_count = crud.get_project(db=db,
                                                   filters=[cellxgene.ProjectMeta.owner == owner,
                                                            cellxgene.ProjectMeta.is_publish != config.ProjectStatus.PROJECT_STATUS_DELETE]
                                                   ).count()
    if already_exist_project_count >= config.NormalUserLimit.MAXPROJECTCOUNT:
        return ResponseMessage(
                    status="0201", data={}, message="Common user has a maximum of three projects"
                )
    publish_status = config.ProjectStatus.PROJECT_STATUS_DRAFT
    create_project_model.members.append(current_user_email_address)
    member_info_list = []
    if create_project_model.is_private:
        member_info_list = crud.get_user(
            db=db,
            filters=[cellxgene.User.email_address.in_(create_project_model.members)],
        ).all()
        if create_project_model.other_file_ids is not None:
            other_file_id_list = create_project_model.other_file_ids.split(",")
            if len(other_file_id_list) > config.ProjectStatus.MAX_OTHER_FILE_NUM:
                return ResponseMessage(
                    status="0201", data={}, message="Project creation failed. Upload up to five other files"
                )
    if create_project_model.is_private and create_project_model.is_publish:
        publish_status = config.ProjectStatus.PROJECT_STATUS_PUBLIC
    insert_project_model = cellxgene.ProjectMeta(
        title=create_project_model.title,
        description=create_project_model.description,
        is_publish=publish_status,
        is_private=create_project_model.is_private,
        tags=create_project_model.tags,
        owner=owner,
    )
    for member_info in member_info_list:
        project_user_model = cellxgene.ProjectUser(user_id=member_info.id)
        insert_project_model.project_project_user_meta.append(project_user_model)
    insert_analysis_model = cellxgene.Analysis(
        h5ad_id=create_project_model.h5ad_id,
        umap_id=create_project_model.umap_id
        if create_project_model.umap_id is not None
        else "",
        cell_marker_id=create_project_model.cell_marker_id
        if create_project_model.cell_marker_id is not None
        else "",
        pathway_id=create_project_model.pathway_id
        if create_project_model.pathway_id is not None
        else "",
        other_file_ids=create_project_model.other_file_ids
        if (
            create_project_model.other_file_ids is not None
            and create_project_model.is_private
        )
        else "",
    )
    insert_analysis_model.analysis_project_meta = insert_project_model
    if not create_project_model.is_private:
        insert_biosample_model = cellxgene.BioSampleMeta(
            species_id=create_project_model.species_id, organ=create_project_model.organ
        )
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
            message="Project creation success",
        )
    except Exception as e:
        print(e)
        return ResponseMessage(status="0201", data={}, message="Project creation failed")


@router.post("/update", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def update_project(
    update_project_model: ProjectUpdateModel,
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
) -> ResponseMessage:
    filter_list = [
        cellxgene.ProjectMeta.id == update_project_model.project_id,
        cellxgene.ProjectMeta.owner == cellxgene.User.id,
        cellxgene.User.email_address == current_user_email_address,
    ]
    project_info = crud.get_project(db=db, filters=filter_list).first()
    update_project_model.members.append(current_user_email_address)
    if not project_info:
        return ResponseMessage(status="0201", data={}, message="permission denied")
    if update_project_model.h5ad_id is not None:
        check_file_name_util.check_file_name(file_type="h5ad", file_id=update_project_model.h5ad_id)
    if update_project_model.umap_id is not None:
        check_file_name_util.check_file_name(file_type="umap", file_id=update_project_model.umap_id)
    if update_project_model.cell_marker_id is not None:
        check_file_name_util.check_file_name(file_type="cell_marker", file_id=update_project_model.cell_marker_id)
    if update_project_model.pathway_id is not None:
        check_file_name_util.check_file_name(file_type="pathway", file_id=update_project_model.pathway_id)
    if (not project_info.is_publish) or project_info.is_private:
        publish_status = config.ProjectStatus.PROJECT_STATUS_DRAFT
        if update_project_model.is_private and update_project_model.is_publish:
            publish_status = config.ProjectStatus.PROJECT_STATUS_IS_PUBLISH
        update_project_dict = {
            "title": update_project_model.title,
            "description": update_project_model.description,
            "tags": update_project_model.tags,
            "is_publish": publish_status,
            "is_private": update_project_model.is_private,
        }
        member_info_list = crud.get_user(
            db=db,
            filters=[cellxgene.User.email_address.in_(update_project_model.members)],
        ).all()
        insert_project_user_model_list = []
        for member_info in member_info_list:
            insert_project_user_model_list.append(
                cellxgene.ProjectUser(
                    project_id=update_project_model.project_id, user_id=member_info.id
                )
            )
        if not project_info.is_private:
            update_biosample_id = project_info.project_project_biosample_meta[
                0
            ].biosample_id
            update_biosample_dict = {
                "species_id": update_project_model.species_id,
                "organ": update_project_model.organ,
            }
        else:
            update_biosample_id = 0
            update_biosample_dict = {}
        update_analysis_id = project_info.project_analysis_meta[0].id
        # h5ad_id = str(uuid4()).replace("-", "")
        update_analysis_dict = {
            "h5ad_id": update_project_model.h5ad_id
            if update_project_model.h5ad_id is not None
            else "",
            "umap_id": update_project_model.umap_id
            if update_project_model.umap_id is not None
            else "",
            "cell_marker_id": update_project_model.cell_marker_id
            if update_project_model.cell_marker_id is not None
            else "",
            "pathway_id": update_project_model.pathway_id
            if update_project_model.pathway_id is not None
            else "",
            "other_file_ids": update_project_model.other_file_ids
            if update_project_model.other_file_ids is not None
            else "",
        }
        crud.project_update_transaction(
            db=db,
            delete_project_user_filters=[
                cellxgene.ProjectUser.project_id == update_project_model.project_id
            ],
            insert_project_user_model_list=insert_project_user_model_list,
            update_project_filters=[
                cellxgene.ProjectMeta.id == update_project_model.project_id
            ],
            update_project_dict=update_project_dict,
            update_biosample_filters=[cellxgene.BioSampleMeta.id == update_biosample_id]
            if not project_info.is_private
            else [],
            update_biosample_dict=update_biosample_dict
            if not project_info.is_private
            else {},
            update_analysis_filters=[cellxgene.Analysis.id == update_analysis_id],
            update_analysis_dict=update_analysis_dict,
        )
    else:
        ResponseMessage(status="0000", data={}, message="Update status exception")
    return ResponseMessage(status="0000", data={}, message="Project update success")


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
        return ResponseMessage(status="0201", data={}, message="permission denied")
    if project_info.is_private:
        is_publish = config.ProjectStatus.PROJECT_STATUS_DRAFT
        try:
            crud.update_project(
                db=db,
                filters=[cellxgene.ProjectMeta.id == project_id],
                update_dict={"is_publish": is_publish},
            )
            return ResponseMessage(status="0000", data={}, message="Project offline successful")
        except:
            return ResponseMessage(status="0201", data={}, message="Project offline failed")
    else:
        return ResponseMessage(status="0201", data={}, message="permission denied")


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
        return ResponseMessage(status="0201", data={}, message="The account of the transfer object does not exist. Please confirm whether the email address is correct")
    project_info = crud.get_project(
        db=db, filters=[cellxgene.ProjectMeta.id == project_id]
    ).first()
    if not project_info:
        return ResponseMessage(status="0201", data={}, message="Project does not exist")
    if project_info.project_user_meta.email_address != current_user_email_address:
        return ResponseMessage(status="0201", data={}, message="You are not the owner of the project and cannot transfer this project")
    already_exist_project_count = crud.get_project(db=db,
                                                   filters=[cellxgene.ProjectMeta.owner == transfer_to_user_info.id,
                                                            cellxgene.ProjectMeta.is_publish != config.ProjectStatus.PROJECT_STATUS_DELETE]
                                                   ).count()
    if already_exist_project_count >= config.NormalUserLimit.MAXPROJECTCOUNT:
        return ResponseMessage(
            status="0201", data={}, message="Common user has a maximum of three projects"
        )
    if project_info.is_private:
        try:
            insert_transfer_model = cellxgene.TransferHistory(
                project_id=project_id,
                old_owner=project_info.owner,
                new_owner=transfer_to_user_info.id,
            )
            crud.create_transfer_history(db=db, insert_model=insert_transfer_model)
            crud.update_project(
                db=db,
                filters=[cellxgene.ProjectMeta.id == project_id],
                update_dict={"owner": transfer_to_user_info.id},
            )
            crud.update_file(
                db=db,
                filters=[cellxgene.Analysis.project_id == project_id],
                file_filters=[
                    cellxgene.Analysis.h5ad_id == cellxgene.FileLibrary.file_id,
                    cellxgene.Analysis.umap_id == cellxgene.FileLibrary.file_id,
                    cellxgene.Analysis.cell_marker_id == cellxgene.FileLibrary.file_id,
                    cellxgene.Analysis.pathway_id == cellxgene.FileLibrary.file_id,
                    cellxgene.Analysis.other_file_ids == cellxgene.FileLibrary.file_id
                ],
                update_dict={"upload_user_id": transfer_to_user_info.id},
            )
            exist_user_id = [
                project_user.user_id
                for project_user in project_info.project_project_user_meta
            ]
            if transfer_to_user_info.id not in exist_user_id:
                crud.create_project_user(
                    db=db,
                    insert_project_user_model=cellxgene.ProjectUser(
                        project_id=project_id, user_id=transfer_to_user_info.id
                    ),
                )
            return ResponseMessage(status="0000", data={}, message="Project transfer success")
        except Exception as e:
            print(e)
            return ResponseMessage(status="0201", data={}, message="Project transfer failed")
    else:
        return ResponseMessage(status="0201", data={}, message="The current state cannot transfer the item")


@router.post(
    "/{project_id}/copy",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
)
def copy_project_id(
    project_id: int,
    copy_to: CopyToProjectModel = Body(),
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
):
    copy_to_user_info = crud.get_user(
        db=db,
        filters=[cellxgene.User.email_address == copy_to.copy_to_email_address],
    ).first()
    if not copy_to_user_info:
        return ResponseMessage(status="0201", data={}, message="The account of the transfer object does not exist. Please confirm whether the email address is correct")
    project_info = crud.get_project(
        db=db, filters=[cellxgene.ProjectMeta.id == project_id]
    ).first()
    if not project_info:
        return ResponseMessage(status="0201", data={}, message="Project does not exist")
    if project_info.project_user_meta.email_address != current_user_email_address:
        return ResponseMessage(status="0201", data={}, message="You are not the owner of the project and cannot copy it")
    already_exist_project_count = crud.get_project(db=db,
                                                   filters=[cellxgene.ProjectMeta.owner == copy_to_user_info.id,
                                                            cellxgene.ProjectMeta.is_publish != config.ProjectStatus.PROJECT_STATUS_DELETE]
                                                   ).count()
    if already_exist_project_count >= config.NormalUserLimit.MAXPROJECTCOUNT:
        return ResponseMessage(
            status="0201", data={}, message="Common user has a maximum of three projects"
        )
    if project_info.is_private == config.ProjectStatus.PROJECT_STATUS_PRIVATE:
        insert_project_dict = project_info.to_dict()
        del insert_project_dict["id"]
        del insert_project_dict["create_at"]
        del insert_project_dict["update_at"]
        insert_project_dict["owner"] = copy_to_user_info.id
        insert_project_model = cellxgene.ProjectMeta(**insert_project_dict)
        insert_project_model.project_project_user_meta = [
            cellxgene.ProjectUser(user_id=copy_to_user_info.id)
        ]
        analysis_meta = project_info.project_analysis_meta[0]
        insert_analysis_dict = analysis_meta.to_dict()
        del insert_analysis_dict["id"]
        del insert_analysis_dict["create_at"]
        del insert_analysis_dict["update_at"]
        if analysis_meta.h5ad_id:
            new_h5ad_id = file_util.copy_file(
                db=db,
                file_ids=analysis_meta.h5ad_id,
                upload_user_id=copy_to_user_info.id,
            )
            insert_analysis_dict["h5ad_id"] = new_h5ad_id
        if analysis_meta.umap_id:
            new_umap_id = file_util.copy_file(
                db=db,
                file_ids=analysis_meta.umap_id,
                upload_user_id=copy_to_user_info.id,
            )
            insert_analysis_dict["umap_id"] = new_umap_id
        if analysis_meta.cell_marker_id:
            new_cell_marker_id = file_util.copy_file(
                db=db,
                file_ids=analysis_meta.cell_marker_id,
                upload_user_id=copy_to_user_info.id,
            )
            insert_analysis_dict["cell_marker_id"] = new_cell_marker_id
        if analysis_meta.pathway_id:
            new_pathway_id = file_util.copy_file(
                db=db,
                file_ids=analysis_meta.pathway_id,
                upload_user_id=copy_to_user_info.id,
            )
            insert_analysis_dict["pathway_id"] = new_pathway_id
        if analysis_meta.other_file_ids:
            new_other_file_ids = file_util.copy_file(
                db=db,
                file_ids=analysis_meta.other_file_ids,
                upload_user_id=copy_to_user_info.id,
            )
            insert_analysis_dict["other_file_ids"] = new_other_file_ids
        insert_analysis_model = cellxgene.Analysis(**insert_analysis_dict)
        insert_analysis_model.analysis_project_meta = insert_project_model
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
                message="Project creation success",
            )
        except Exception as e:
            print(e)
            return ResponseMessage(status="0201", data={}, message="Project creation failed")
    else:
        return ResponseMessage(status="0201", data={}, message="The project cannot be copied in the current state")


@router.get(
    "/organ/list", response_model=ResponseMessage, status_code=status.HTTP_200_OK
)
async def get_organ_list(
    organ: Union[str, None] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    # current_user_email_address=Depends(get_current_user),
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
    order_by: Union[str, None] = None,
    asc: Union[bool, None] = None,
    species_id: Union[int, None] = None,
    organ: Union[str, None] = None,
    external_sample_accesstion: Union[str, None] = None,
    disease: Union[str, None] = None,
    development_stage: Union[str, None] = None,
    biosample_type: Union[str, None] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    # current_user_email_address=Depends(get_current_user),
) -> ResponseMessage:
    search_page = (page - 1) * page_size
    project_list = []
    # filter_list = [
    #     cellxgene.BioSampleMeta.id == cellxgene.ProjectBioSample.biosample_id,
    #     cellxgene.ProjectBioSample.project_id == cellxgene.ProjectUser.project_id,
    #     cellxgene.ProjectUser.user_id == cellxgene.User.id,
    #     cellxgene.User.email_address == current_user_email_address,
    # ]
    public_filter_list = [
        cellxgene.BioSampleMeta.id == cellxgene.ProjectBioSample.biosample_id,
        cellxgene.ProjectBioSample.project_id == cellxgene.ProjectMeta.id,
        cellxgene.ProjectMeta.is_publish
        == config.ProjectStatus.PROJECT_STATUS_IS_PUBLISH,
        cellxgene.ProjectMeta.is_private == config.ProjectStatus.PROJECT_STATUS_PUBLIC,
    ]
    if species_id is not None:
        public_filter_list.append(cellxgene.BioSampleMeta.species_id == species_id)
    if organ is not None:
        # filter_list.append(cellxgene.BioSampleMeta.organ == organ)
        public_filter_list.append(cellxgene.BioSampleMeta.organ == organ)
    if external_sample_accesstion is not None:
        # filter_list.append(
        #     cellxgene.BioSampleMeta.external_sample_accesstion
        #     == external_sample_accesstion
        # )
        public_filter_list.append(
            cellxgene.BioSampleMeta.external_sample_accesstion
            == external_sample_accesstion
        )
    if disease is not None:
        # filter_list.append(cellxgene.BioSampleMeta.disease.like("%{}%".format(disease)))
        public_filter_list.append(
            cellxgene.BioSampleMeta.disease.like("%{}%".format(disease))
        )
    if development_stage is not None:
        # filter_list.append(
        #     cellxgene.BioSampleMeta.development_stage.like(
        #         "%{}%".format(development_stage)
        #     )
        # )
        public_filter_list.append(
            cellxgene.BioSampleMeta.development_stage.like(
                "%{}%".format(development_stage)
            )
        )
    if biosample_type is not None:
        public_filter_list.append(
            cellxgene.BioSampleMeta.biosample_type == biosample_type
        )
    if order_by is not None:
        orderby_list = order_by.split(".")
        orderby_orm = table_config.cellxgene_table_dict.get(orderby_list[0]).get(
            orderby_list[1]
        )
        if asc:
            biosample_list = (
                crud.get_project_by_sample_join(
                    db=db,
                    query_list=[
                        cellxgene.BioSampleMeta,
                        cellxgene.Analysis,
                        cellxgene.ProjectMeta,
                        cellxgene.DonorMeta,
                        cellxgene.SpeciesMeta
                    ],
                    public_filter_list=public_filter_list,
                )
                .distinct()
                .order_by(orderby_orm.asc())
                .offset(search_page)
                .limit(page_size)
                .all()
            )
        else:
            biosample_list = (
                crud.get_project_by_sample_join(
                    db=db,
                    query_list=[
                        cellxgene.BioSampleMeta,
                        cellxgene.Analysis,
                        cellxgene.ProjectMeta,
                        cellxgene.DonorMeta,
                        cellxgene.SpeciesMeta
                    ],
                    public_filter_list=public_filter_list,
                )
                .distinct()
                .order_by(orderby_orm.desc())
                .offset(search_page)
                .limit(page_size)
                .all()
            )
    else:
        biosample_list = (
            crud.get_project_by_sample_join(
                db=db,
                query_list=[
                    cellxgene.BioSampleMeta,
                    cellxgene.Analysis,
                    cellxgene.ProjectMeta,
                    cellxgene.DonorMeta,
                    cellxgene.SpeciesMeta
                ],
                public_filter_list=public_filter_list,
            )
            .distinct()
            .offset(search_page)
            .limit(page_size)
            .all()
        )
    for biosample_meta_list in biosample_list:
        project_dict = {}
        biosample_meta = dict_util.row2dict(biosample_meta_list[0])
        analysis_meta = dict_util.row2dict(biosample_meta_list[1])
        project_meta = dict_util.row2dict(biosample_meta_list[2])
        donor_meta = dict_util.row2dict(biosample_meta_list[3])
        species_meta = dict_util.row2dict(biosample_meta_list[4])
        project_dict["analysis_meta"] = analysis_meta
        project_dict["project_meta"] = project_meta
        project_dict["biosample_meta"] = biosample_meta
        project_dict["donor_meta"] = donor_meta
        project_dict["species_meta"] = species_meta
        project_list.append(project_dict)
    total = (
        crud.get_project_by_sample_join(
            db=db, query_list=[func.count(1)], public_filter_list=public_filter_list
        )
        .distinct()
        .first()
    )[0]
    res_dict = {
        "project_list": project_list,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    return ResponseMessage(status="0000", data=res_dict, message="ok")


@router.get(
    "/list/by/sample/download",
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def download_project_list_by_sample(
    species_id: Union[int, None] = None,
    organ: Union[str, None] = None,
    external_sample_accesstion: Union[str, None] = None,
    disease: Union[str, None] = None,
    development_stage: Union[str, None] = None,
    db: Session = Depends(get_db),
    # current_user_email_address=Depends(get_current_user),
):
    page_size = 5000
    public_filter_list = [
        cellxgene.BioSampleMeta.id == cellxgene.ProjectBioSample.biosample_id,
        cellxgene.ProjectBioSample.project_id == cellxgene.ProjectMeta.id,
        cellxgene.ProjectMeta.is_publish
        == config.ProjectStatus.PROJECT_STATUS_IS_PUBLISH,
        cellxgene.ProjectMeta.is_private == config.ProjectStatus.PROJECT_STATUS_PUBLIC,
    ]
    if organ is not None:
        # filter_list.append(cellxgene.BioSampleMeta.organ == organ)
        public_filter_list.append(cellxgene.BioSampleMeta.organ == organ)
    if species_id is not None:
        # filter_list.append(cellxgene.BioSampleMeta.species_id == species_id)
        public_filter_list.append(cellxgene.BioSampleMeta.species_id == species_id)
    if external_sample_accesstion is not None:
        public_filter_list.append(
            cellxgene.BioSampleMeta.external_sample_accesstion
            == external_sample_accesstion
        )
    if disease is not None:
        public_filter_list.append(
            cellxgene.BioSampleMeta.disease.like("%{}%".format(disease))
        )
    if development_stage is not None:
        public_filter_list.append(
            cellxgene.BioSampleMeta.development_stage.like(
                "%{}%".format(development_stage)
            )
        )
    biosample_list = (
        crud.get_project_by_sample_join(
            db=db,
            query_list=[
                cellxgene.BioSampleMeta,
                cellxgene.Analysis,
                cellxgene.ProjectMeta,
                cellxgene.DonorMeta,
                cellxgene.SpeciesMeta
            ],
            public_filter_list=public_filter_list,
        )
        .distinct()
        .limit(page_size)
        .all()
    )
    data_list = []
    for biosample_meta_list in biosample_list:
        project_dict = {}
        project_meta = dict_util.row2dict(biosample_meta_list[2])
        for key, value in project_meta.items():
            project_dict["project_" + key] = value
        analysis_meta = dict_util.row2dict(biosample_meta_list[1])
        for key, value in analysis_meta.items():
            project_dict["analysis_" + key] = value
        biosample_meta = dict_util.row2dict(biosample_meta_list[0])
        for key, value in biosample_meta.items():
            project_dict["biosample_" + key] = value
        donor_meta = dict_util.row2dict(biosample_meta_list[3])
        for key, value in donor_meta.items():
            project_dict["donor_" + key] = value if value else ""
        species_meta = dict_util.row2dict(biosample_meta_list[4])
        for key, value in species_meta.items():
            project_dict["species_" + key] = value if value else ""
        data_list.append(project_dict)
    data_df = pd.DataFrame(
        data=data_list,
    )
    data_df = data_df.fillna("")
    buffer = BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet()
    for i, col in enumerate(data_df.columns):
        worksheet.write(0, i, col)
        for j, value in enumerate(data_df[col]):
            worksheet.write(j + 1, i, value)
    workbook.close()

    # 将 Excel 文件转换为字节流，作为响应体返回给客户端
    buffer.seek(0)
    excel_bytes = buffer.getvalue()
    return StreamingResponse(
        BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=myfile.xlsx"},
    )


@router.get(
    "/list/by/cell",
    response_model=ResponseProjectListModel,
    status_code=status.HTTP_200_OK,
)
async def get_project_list_by_cell(
    species_id: int,
    order_by: Union[str, None] = None,
    asc: Union[bool, None] = None,
    ct_id: Union[str, None] = None,
    cl_id: Union[str, None] = None,
    cell_standard: Union[str, None] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    # current_user_email_address=Depends(get_current_user),
) -> ResponseMessage:
    search_page = (page - 1) * page_size
    project_list = []
    # filter_list = [
    #     cellxgene.CellTypeMeta.cell_type_id
    #     == cellxgene.CalcCellClusterProportion.cell_type_id,
    #     cellxgene.CalcCellClusterProportion.analysis_id == cellxgene.Analysis.id,
    #     cellxgene.Analysis.project_id == cellxgene.ProjectUser.project_id,
    #     cellxgene.ProjectUser.user_id == cellxgene.User.id,
    #     cellxgene.User.email_address == current_user_email_address,
    # ]
    public_filter_list = [
        cellxgene.CellTypeMeta.cell_type_id
        == cellxgene.CalcCellClusterProportion.cell_type_id,
        cellxgene.CellTypeMeta.species_id == species_id,
        cellxgene.CalcCellClusterProportion.analysis_id == cellxgene.Analysis.id,
        cellxgene.Analysis.project_id == cellxgene.ProjectMeta.id,
        cellxgene.ProjectMeta.is_publish
        == config.ProjectStatus.PROJECT_STATUS_IS_PUBLISH,
        cellxgene.ProjectMeta.is_private == config.ProjectStatus.PROJECT_STATUS_PUBLIC,
    ]
    if ct_id is not None:
        ct_id_list = ct_id.split(",")
        # filter_list.append(cellxgene.CellTypeMeta.cell_type_id == cell_id)
        public_filter_list.append(cellxgene.CellTypeMeta.cell_type_id.in_(ct_id_list))
    if cl_id is not None:
        cl_id_list = cl_id.split(",")
        public_filter_list.append(cellxgene.CellTypeMeta.cell_ontology_id.in_(cl_id_list))
    if cell_standard is not None:
        cell_standard_filter_list = [
            cellxgene.CellTaxonomy.ct_id == cellxgene.CellTypeMeta.cell_taxonomy_id,
            cellxgene.CellTaxonomy.cell_standard.like("%{}%".format(cell_standard)),
        ]
        public_filter_list.append(and_(*cell_standard_filter_list))
    if order_by is not None:
        orderby_list = order_by.split(".")
        orderby_orm = table_config.cellxgene_table_dict.get(orderby_list[0]).get(
            orderby_list[1]
        )
        if asc:
            cell_proportion_list = (
                crud.get_project_by_cell_join_for_search(
                    db=db,
                    query_list=[
                        cellxgene.CalcCellClusterProportion,
                        cellxgene.Analysis,
                        cellxgene.ProjectMeta,
                        cellxgene.BioSampleMeta,
                        cellxgene.CellTypeMeta,
                        cellxgene.DonorMeta,
                        cellxgene.SpeciesMeta
                    ],
                    public_filter_list=public_filter_list,
                    species_id=species_id
                )
                .distinct()
                .order_by(orderby_orm.asc())
                .offset(search_page)
                .limit(page_size)
                .all()
            )
        else:
            cell_proportion_list = (
                crud.get_project_by_cell_join_for_search(
                    db=db,
                    query_list=[
                        cellxgene.CalcCellClusterProportion,
                        cellxgene.Analysis,
                        cellxgene.ProjectMeta,
                        cellxgene.BioSampleMeta,
                        cellxgene.CellTypeMeta,
                        cellxgene.DonorMeta,
                        cellxgene.SpeciesMeta
                    ],
                    public_filter_list=public_filter_list,
                    species_id=species_id
                )
                .distinct()
                .order_by(orderby_orm.desc())
                .offset(search_page)
                .limit(page_size)
                .all()
            )
    else:
        cell_proportion_list = (
            crud.get_project_by_cell_join_for_search(
                db=db,
                query_list=[
                    cellxgene.CalcCellClusterProportion,
                    cellxgene.Analysis,
                    cellxgene.ProjectMeta,
                    cellxgene.BioSampleMeta,
                    cellxgene.CellTypeMeta,
                    cellxgene.DonorMeta,
                    cellxgene.SpeciesMeta
                ],
                public_filter_list=public_filter_list,
                species_id=species_id
            )
            .distinct()
            .offset(search_page)
            .limit(page_size)
            .all()
        )
    for cell_proportion_meta_list in cell_proportion_list:
        project_dict = {}
        cell_proportion_meta = dict_util.row2dict(cell_proportion_meta_list[0])
        analysis_meta = dict_util.row2dict(cell_proportion_meta_list[1])
        project_meta = dict_util.row2dict(cell_proportion_meta_list[2])
        biosample_meta = dict_util.row2dict(cell_proportion_meta_list[3])
        cell_type_meta = dict_util.row2dict(cell_proportion_meta_list[4])
        donor_meta = dict_util.row2dict(cell_proportion_meta_list[5])
        species_meta = dict_util.row2dict(cell_proportion_meta_list[6])
        project_dict["cell_proportion_meta"] = cell_proportion_meta
        project_dict["analysis_meta"] = analysis_meta
        project_dict["project_meta"] = project_meta
        project_dict["biosample_meta"] = biosample_meta
        project_dict["cell_type_meta"] = cell_type_meta
        project_dict["donor_meta"] = donor_meta
        project_dict["species_meta"] = species_meta
        project_list.append(project_dict)
    total = (
        crud.get_project_by_cell_join_for_search(
            db=db,
            query_list=[func.count(1)],
            public_filter_list=public_filter_list,
            species_id=species_id
        )
        .distinct()
        .first()
    )[0]
    res_dict = {
        "project_list": project_list,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    return ResponseMessage(status="0000", data=res_dict, message="ok")


@router.get(
    "/list/by/cell/download",
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def download_project_list_by_cell(
    species_id: int,
    ct_id: Union[str, None] = None,
    cl_id: Union[str, None] = None,
    cell_standard: Union[str, None] = None,
    db: Session = Depends(get_db),
    # current_user_email_address=Depends(get_current_user),
):
    page_size = 5000
    public_filter_list = [
        cellxgene.CellTypeMeta.cell_type_id
        == cellxgene.CalcCellClusterProportion.cell_type_id,
        cellxgene.CellTypeMeta.species_id == species_id,
        cellxgene.CalcCellClusterProportion.analysis_id == cellxgene.Analysis.id,
        cellxgene.Analysis.project_id == cellxgene.ProjectMeta.id,
        cellxgene.ProjectMeta.is_publish
        == config.ProjectStatus.PROJECT_STATUS_IS_PUBLISH,
        cellxgene.ProjectMeta.is_private == config.ProjectStatus.PROJECT_STATUS_PUBLIC,
    ]
    if ct_id is not None:
        ct_id_list = ct_id.split(",")
        public_filter_list.append(cellxgene.CellTypeMeta.cell_type_id.in_(ct_id_list))
    if cl_id is not None:
        cl_id_list = cl_id.split(",")
        public_filter_list.append(cellxgene.CellTypeMeta.cell_ontology_id.in_(cl_id_list))
    if cell_standard is not None:
        cell_standard_filter_list = [
            cellxgene.CellTaxonomy.ct_id == cellxgene.CellTypeMeta.cell_taxonomy_id,
            cellxgene.CellTaxonomy.cell_standard.like("%{}%".format(cell_standard)),
        ]
        public_filter_list.append(and_(*cell_standard_filter_list))
    cell_proportion_list = (
        crud.get_project_by_cell_join_for_search(
            db=db,
            query_list=[
                cellxgene.CalcCellClusterProportion,
                cellxgene.Analysis,
                cellxgene.ProjectMeta,
                cellxgene.BioSampleMeta,
                cellxgene.CellTypeMeta,
                cellxgene.DonorMeta,
                cellxgene.SpeciesMeta
            ],
            public_filter_list=public_filter_list,
            species_id=species_id
        )
        .distinct()
        .limit(page_size)
        .all()
    )
    data_list = []
    for cell_proportion_meta_list in cell_proportion_list:
        project_dict = {}
        project_meta = dict_util.row2dict(cell_proportion_meta_list[2])
        for key, value in project_meta.items():
            project_dict["project_" + key] = value
        analysis_meta = dict_util.row2dict(cell_proportion_meta_list[1])
        for key, value in analysis_meta.items():
            project_dict["analysis_" + key] = value
        biosample_meta = dict_util.row2dict(cell_proportion_meta_list[3])
        for key, value in biosample_meta.items():
            project_dict["biosample_" + key] = value
        cell_proportion_meta = dict_util.row2dict(cell_proportion_meta_list[0])
        for key, value in cell_proportion_meta.items():
            project_dict["cell_proportion_" + key] = value
        cell_type_meta = dict_util.row2dict(cell_proportion_meta_list[4])
        for key, value in cell_type_meta.items():
            project_dict["cell_type_" + key] = value
        donor_meta = dict_util.row2dict(cell_proportion_meta_list[5])
        for key, value in donor_meta.items():
            project_dict["donor_" + key] = value if value else ""
        species_meta = dict_util.row2dict(cell_proportion_meta_list[6])
        for key, value in species_meta.items():
            project_dict["species_" + key] = value if value else ""
        data_list.append(project_dict)
    data_df = pd.DataFrame(
        data=data_list,
    )
    data_df = data_df.fillna("")
    buffer = BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet()
    for i, col in enumerate(data_df.columns):
        worksheet.write(0, i, col)
        for j, value in enumerate(data_df[col]):
            worksheet.write(j + 1, i, value)
    workbook.close()

    # 将 Excel 文件转换为字节流，作为响应体返回给客户端
    buffer.seek(0)
    excel_bytes = buffer.getvalue()
    return StreamingResponse(
        BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=myfile.xlsx"},
    )


@router.get(
    "/list/by/gene",
    response_model=ResponseProjectListModel,
    status_code=status.HTTP_200_OK,
)
async def get_project_list_by_gene(
    species_id: int,
    gene_symbol: str,
    order_by: Union[str, None] = None,
    asc: Union[bool, None] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    # current_user_email_address=Depends(get_current_user),
) -> ResponseMessage:
    search_page = (page - 1) * page_size
    project_list = []
    # filter_list = [
    #     cellxgene.GeneMeta.gene_ensemble_id
    #     == cellxgene.CellClusterGeneExpression.gene_ensemble_id,
    #     cellxgene.CellClusterGeneExpression.calculated_cell_cluster_id
    #     == cellxgene.CalcCellClusterProportion.calculated_cell_cluster_id,
    #     cellxgene.CalcCellClusterProportion.analysis_id == cellxgene.Analysis.id,
    #     cellxgene.Analysis.project_id == cellxgene.ProjectUser.project_id,
    #     cellxgene.ProjectUser.user_id == cellxgene.User.id,
    #     cellxgene.User.email_address == current_user_email_address,
    # ]
    public_filter_list = [
        cellxgene.GeneMeta.species_id == species_id,
        cellxgene.GeneMeta.gene_ensemble_id
        == cellxgene.CellClusterGeneExpression.gene_ensemble_id,
        cellxgene.CellClusterGeneExpression.analysis_id == cellxgene.Analysis.id,
        cellxgene.Analysis.project_id == cellxgene.ProjectMeta.id,
        cellxgene.ProjectMeta.is_publish
        == config.ProjectStatus.PROJECT_STATUS_IS_PUBLISH,
        cellxgene.ProjectMeta.is_private == config.ProjectStatus.PROJECT_STATUS_PUBLIC,
    ]
    if gene_symbol is not None:
        # filter_list.append(
        #     cellxgene.GeneMeta.gene_symbol.like("%{}%".format(gene_symbol))
        # )
        public_filter_list.append(
            cellxgene.GeneMeta.gene_symbol.like("%{}%".format(gene_symbol))
        )
    if order_by is not None:
        orderby_list = order_by.split(".")
        orderby_orm = table_config.cellxgene_table_dict.get(orderby_list[0]).get(
            orderby_list[1]
        )
        if asc:
            gene_meta_list = (
                crud.get_project_by_gene_join(
                    db=db,
                    query_list=[
                        cellxgene.CellClusterGeneExpression,
                        cellxgene.Analysis,
                        cellxgene.ProjectMeta,
                        cellxgene.CellTypeMeta,
                        cellxgene.SpeciesMeta
                    ],
                    # filters=filter_list,
                    public_filter_list=public_filter_list,
                    species_id=species_id
                )
                .distinct()
                .order_by(orderby_orm.asc())
                .offset(search_page)
                .limit(page_size)
                .all()
            )
        else:
            gene_meta_list = (
                crud.get_project_by_gene_join(
                    db=db,
                    query_list=[
                        cellxgene.CellClusterGeneExpression,
                        cellxgene.Analysis,
                        cellxgene.ProjectMeta,
                        cellxgene.CellTypeMeta,
                        cellxgene.SpeciesMeta
                    ],
                    # filters=filter_list,
                    public_filter_list=public_filter_list,
                    species_id=species_id
                )
                .distinct()
                .order_by(orderby_orm.desc())
                .offset(search_page)
                .limit(page_size)
                .all()
            )
    else:
        gene_meta_list = (
            crud.get_project_by_gene_join(
                db=db,
                query_list=[
                    cellxgene.CellClusterGeneExpression,
                    cellxgene.Analysis,
                    cellxgene.ProjectMeta,
                    cellxgene.CellTypeMeta,
                    cellxgene.SpeciesMeta
                ],
                # filters=filter_list,
                public_filter_list=public_filter_list,
                species_id=species_id
            )
            .distinct()
            # .order_by(cellxgene.BioSampleMeta.id.asc())
            .offset(search_page)
            .limit(page_size)
            .all()
        )
    for gene_meta in gene_meta_list:
        project_dict = {}
        gene_expression_meta = dict_util.row2dict(gene_meta[0])
        analysis_meta = dict_util.row2dict(gene_meta[1])
        project_meta = dict_util.row2dict(gene_meta[2])
        cell_type_meta = dict_util.row2dict(gene_meta[3])
        species_meta = dict_util.row2dict(gene_meta[4])
        project_dict["gene_expression_meta"] = gene_expression_meta
        project_dict["analysis_meta"] = analysis_meta
        project_dict["project_meta"] = project_meta
        project_dict["cell_type_meta"] = cell_type_meta
        project_dict["species_meta"] = species_meta
        project_list.append(project_dict)
    total = (
        crud.get_project_by_gene_join(
            db=db,
            query_list=[func.count(1)],
            public_filter_list=public_filter_list,
            species_id=species_id
        )
        .distinct()
        .first()
    )[0]
    res_dict = {
        "project_list": project_list,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    return ResponseMessage(status="0000", data=res_dict, message="ok")


@router.get(
    "/list/by/gene/download",
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def download_project_list_by_gene(
    species_id: int,
    gene_symbol: str,
    db: Session = Depends(get_db),
):
    page_size = 5000
    public_filter_list = [
        cellxgene.GeneMeta.species_id == species_id,
        cellxgene.GeneMeta.gene_ensemble_id
        == cellxgene.CellClusterGeneExpression.gene_ensemble_id,
        cellxgene.CellClusterGeneExpression.analysis_id == cellxgene.Analysis.id,
        cellxgene.Analysis.project_id == cellxgene.ProjectMeta.id,
        cellxgene.ProjectMeta.is_publish
        == config.ProjectStatus.PROJECT_STATUS_IS_PUBLISH,
        cellxgene.ProjectMeta.is_private == config.ProjectStatus.PROJECT_STATUS_PUBLIC,
    ]
    if gene_symbol is not None:
        public_filter_list.append(
            cellxgene.GeneMeta.gene_symbol.like("%{}%".format(gene_symbol))
        )
    gene_list = (
        crud.get_project_by_gene_join(
            db=db,
            query_list=[
                cellxgene.CellClusterGeneExpression,
                cellxgene.Analysis,
                cellxgene.ProjectMeta,
                cellxgene.CellTypeMeta,
                cellxgene.SpeciesMeta
            ],
            public_filter_list=public_filter_list,
            species_id=species_id
        )
        .distinct()
        .limit(page_size)
        .all()
    )
    data_list = []
    for gene_meta_list in gene_list:
        project_dict = {}
        project_meta = dict_util.row2dict(gene_meta_list[2])
        for key, value in project_meta.items():
            project_dict["project_" + key] = value
        analysis_meta = dict_util.row2dict(gene_meta_list[1])
        for key, value in analysis_meta.items():
            project_dict["analysis_" + key] = value
        cell_type_meta = dict_util.row2dict(gene_meta_list[3])
        for key, value in cell_type_meta.items():
            project_dict["cell_type_" + key] = value
        gene_expression_meta = dict_util.row2dict(gene_meta_list[0])
        for key, value in gene_expression_meta.items():
            project_dict["cell_proportion_" + key] = value
        species_meta = dict_util.row2dict(gene_meta_list[4])
        for key, value in species_meta.items():
            project_dict["species_" + key] = value if value else ""
        data_list.append(project_dict)
    data_df = pd.DataFrame(
        data=data_list,
    )
    data_df = data_df.fillna("")
    buffer = BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet()
    for i, col in enumerate(data_df.columns):
        worksheet.write(0, i, col)
        for j, value in enumerate(data_df[col]):
            worksheet.write(j + 1, i, value)
    workbook.close()

    # 将 Excel 文件转换为字节流，作为响应体返回给客户端
    buffer.seek(0)
    excel_bytes = buffer.getvalue()
    return StreamingResponse(
        BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=myfile.xlsx"},
    )


@router.get(
    "/list/by/gene/graph",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
)
async def get_project_list_graph_by_gene(
    species_id: int,
    gene_symbol: Union[str, None] = None,
    db: Session = Depends(get_db),
    # current_user_email_address=Depends(get_current_user),
) -> ResponseMessage:
    # filter_list = [
    #     cellxgene.GeneMeta.gene_ensemble_id
    #     == cellxgene.CellClusterGeneExpression.gene_ensemble_id,
    #     cellxgene.CellClusterGeneExpression.calculated_cell_cluster_id
    #     == cellxgene.CalcCellClusterProportion.calculated_cell_cluster_id,
    #     cellxgene.CalcCellClusterProportion.analysis_id == cellxgene.Analysis.id,
    #     cellxgene.Analysis.project_id == cellxgene.ProjectUser.project_id,
    #     cellxgene.ProjectUser.user_id == cellxgene.User.id,
    #     cellxgene.User.email_address == current_user_email_address,
    # ]
    public_filter_list = [
        cellxgene.GeneMeta.gene_ensemble_id
        == cellxgene.CellClusterGeneExpression.gene_ensemble_id,
        cellxgene.CellClusterGeneExpression.analysis_id == cellxgene.Analysis.id,
        cellxgene.Analysis.project_id == cellxgene.ProjectMeta.id,
        cellxgene.ProjectMeta.is_publish
        == config.ProjectStatus.PROJECT_STATUS_IS_PUBLISH,
        cellxgene.ProjectMeta.is_private == config.ProjectStatus.PROJECT_STATUS_PUBLIC,
    ]
    if gene_symbol is not None:
        # filter_list.append(
        #     cellxgene.GeneMeta.gene_symbol.like("%{}%".format(gene_symbol))
        # )
        public_filter_list.extend(
            [cellxgene.GeneMeta.gene_symbol.like("%{}%".format(gene_symbol))]
        )
    if species_id is not None:
        # filter_list.append(cellxgene.GeneMeta.species_id == species_id)
        public_filter_list.extend(
            [
                cellxgene.GeneMeta.species_id == species_id,
                cellxgene.CellClusterGeneExpression.cell_type_id
                == cellxgene.CellTypeMeta.cell_type_id,
                cellxgene.CellTypeMeta.species_id == species_id,
            ]
        )
    gene_meta_list = (
        crud.get_project_by_gene(
            db=db,
            query_list=[
                cellxgene.CellClusterGeneExpression.cell_proportion_expression_the_gene,
                cellxgene.CellClusterGeneExpression.average_gene_expression,
                cellxgene.CellTypeMeta.cell_type_name,
            ],
            # filters=filter_list,
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


@router.get(
    "/{analysis_id}/graph/cell_number",
    response_model=ResponseProjectDetailModel,
    status_code=status.HTTP_200_OK,
)
async def view_cell_number_graph(
    analysis_id: int,
    db: Session = Depends(get_db),
    # current_user_email_address=Depends(get_current_user),
):
    cell_proportion_meta_list = crud.get_cell_proportion(
        db=db,
        query_list=[cellxgene.CalcCellClusterProportion],
        filters=[cellxgene.CalcCellClusterProportion.analysis_id == analysis_id],
    )
    return ResponseMessage(status="0000", data=cell_proportion_meta_list, message="ok")


@router.get(
    "/{analysis_id}/graph/pathway",
    response_model=ResponseProjectDetailModel,
    status_code=status.HTTP_200_OK,
)
async def view_pathway_graph(
    analysis_id: int,
    db: Session = Depends(get_db),
    # current_user_email_address=Depends(get_current_user),
):
    pathway_meta_list = crud.get_pathway_score(
        db=db, filters=[cellxgene.PathwayScore.analysis_id == analysis_id]
    )
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
    file_id = await file_util.save_file(db=db, file=file, insert_user_model=current_user_info)
    if file_id:
        return ResponseMessage(status="0000", data={}, message="File upload success")


@router.get(
    "/file/me",
    response_model=ResponseProjectListModel,
    status_code=status.HTTP_200_OK,
)
async def get_user_h5ad_file_list(
    file_name: Union[str, None] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
):
    search_page = (page - 1) * page_size
    filter_list = [
        cellxgene.User.email_address == current_user_email_address,
        cellxgene.FileLibrary.upload_user_id == cellxgene.User.id,
        cellxgene.FileLibrary.file_status == config.FileStatus.NORMAL
    ]
    if file_name:
        filter_list.append(
            cellxgene.FileLibrary.file_name.like("%{}%".format(file_name))
        )
    h5ad_file_list = (
        crud.get_file_info(db=db, query_list=[cellxgene.FileLibrary], filters=filter_list)
        .order_by(cellxgene.FileLibrary.create_at.desc())
        .offset(search_page)
        .limit(page_size)
        .all()
    )
    total = crud.get_file_info(db=db, query_list=[cellxgene.FileLibrary], filters=filter_list).count()
    res_dict = {
        "h5ad_list": h5ad_file_list,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    return ResponseMessage(status="0000", data=res_dict, message="ok")


@router.delete(
    '/file/{file_id}',
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK
)
async def delete_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
):
    filter_list = [
        cellxgene.User.email_address == current_user_email_address,
        cellxgene.FileLibrary.upload_user_id == cellxgene.User.id,
        cellxgene.FileLibrary.file_id == file_id
    ]
    file_info = (
        crud.get_file_info(db=db, query_list=[cellxgene.FileLibrary], filters=filter_list)
        .first()
    )
    if not file_info:
        return ResponseMessage(status="0201", data={}, message="permission denied")
    analysis_filter_list = [
        cellxgene.Analysis.project_id == cellxgene.ProjectMeta.id,
        cellxgene.ProjectMeta.is_publish != config.ProjectStatus.PROJECT_STATUS_DELETE,
        or_(cellxgene.Analysis.umap_id == file_id,
            cellxgene.Analysis.cell_marker_id == file_id,
            cellxgene.Analysis.excel_id == file_id,
            cellxgene.Analysis.pathway_id == file_id,
            cellxgene.Analysis.h5ad_id == file_id,
            cellxgene.Analysis.other_file_ids.like("%{}%".format(file_id)))
    ]
    analysis_info = crud.get_analysis(db=db, filters=analysis_filter_list).first()
    if not analysis_info:
        file_util.remove_file(file_id)
        crud.update_file(db=db, filters=[cellxgene.FileLibrary.file_id == file_id], file_filters=[], update_dict={"file_status": config.FileStatus.DELETE})
        return ResponseMessage(status="0000", data={}, message="ok")
    else:
        return ResponseMessage(status="0201", data={}, message="The file is associated with an item and cannot be deleted")


@router.get(
    "/species/list",
    response_model=ResponseProjectListModel,
    status_code=status.HTTP_200_OK,
)
async def get_species_list(db: Session = Depends(get_db)) -> ResponseMessage:
    species_list = crud.get_species_list(
        db=db, query_list=[cellxgene.SpeciesMeta], filters=[]
    ).all()
    return ResponseMessage(status="0000", data=species_list, message="ok")


@router.get(
    "/sample/list",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
)
async def get_biosample_list(
    organ: Union[str, None] = None,
    disease: Union[str, None] = None,
    development_stage: Union[str, None] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
) -> ResponseMessage:
    search_page = (page - 1) * page_size

    public_filter_list = [
        cellxgene.BioSampleMeta.id == cellxgene.ProjectBioSample.biosample_id,
        cellxgene.ProjectBioSample.project_id == cellxgene.ProjectMeta.id,
        cellxgene.ProjectMeta.is_publish
        == config.ProjectStatus.PROJECT_STATUS_IS_PUBLISH,
        cellxgene.ProjectMeta.is_private == config.ProjectStatus.PROJECT_STATUS_PUBLIC,
    ]
    query_list = [cellxgene.BioSampleMeta]
    if organ is not None:
        # filter_list.append(cellxgene.BioSampleMeta.organ == organ)
        public_filter_list.append(cellxgene.BioSampleMeta.organ.like(
                "%{}%".format(organ)
            ))
        query_list = [cellxgene.BioSampleMeta.organ]
    if disease is not None:
        # filter_list.append(cellxgene.BioSampleMeta.disease.like("%{}%".format(disease)))
        public_filter_list.append(
            cellxgene.BioSampleMeta.disease.like("%{}%".format(disease))
        )
        query_list = [cellxgene.BioSampleMeta.disease]
    if development_stage is not None:
        public_filter_list.append(
            cellxgene.BioSampleMeta.development_stage.like(
                "%{}%".format(development_stage)
            )
        )
        query_list = [cellxgene.BioSampleMeta.development_stage]
    biosample_meta_list = crud.get_biosample(db=db, query_list=query_list, filters=public_filter_list).distinct().offset(search_page).limit(page_size).all()
    res_list = [biosample_meta[0] for biosample_meta in biosample_meta_list]
    total = crud.get_biosample(db=db, query_list=query_list, filters=public_filter_list).distinct().count()
    res_dict = {
        "biosample_list": res_list,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    return ResponseMessage(status="0000", data=res_dict, message="ok")


@router.get(
    "/cell_type/list",
    response_model=ResponseProjectListModel,
    status_code=status.HTTP_200_OK,
)
async def get_cell_type_list(
    species_id: int,
    cell_type_id: str,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
) -> ResponseMessage:
    search_page = (page - 1) * page_size
    cell_type_list = crud.get_cell_type_meta(
        db=db, query_list=[cellxgene.CellTypeMeta], filters=[cellxgene.CellTypeMeta.cell_type_id.like("%{}%".format(cell_type_id)),
                                                             cellxgene.CellTypeMeta.species_id == species_id]
    ).offset(search_page).limit(page_size).all()
    total = crud.get_cell_type_meta(
        db=db, query_list=[cellxgene.CellTypeMeta], filters=[cellxgene.CellTypeMeta.cell_type_id.like("%{}%".format(cell_type_id)),
                                                             cellxgene.CellTypeMeta.species_id == species_id]
    ).count()
    res_dict = {
        "cell_type_list": cell_type_list,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    return ResponseMessage(status="0000", data=res_dict, message="ok")


@router.get(
    "/view/tree/cell_taxonomy",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
)
async def get_cell_taxonomy_tree(
    # cell_marker: str,
    cell_standard: Union[str, None] = None,
    cell_type_id: Union[str, None] = None,
    db: Session = Depends(get_db),
    # current_user_email_address = Depends(get_current_user),
):
    filter_list, public_filter_list = [], []
    if cell_standard:
        or_cell_standard = cell_standard.replace("-", " ")
        filter_list = [
            cellxgene.CellTaxonomy.specific_cell_ontology_id
            == cellxgene.CellTaxonomyRelation.cl_id,
            cellxgene.CellTaxonomy.cell_standard.op("regexp")("\\b{}\\b".format(cell_standard)),
        ]
        public_filter_list = [
            cellxgene.CellTaxonomy.specific_cell_ontology_id
            == cellxgene.CellTaxonomyRelation.cl_id,
            cellxgene.CellTaxonomy.cell_standard.op("regexp")("\\b{}\\b".format(or_cell_standard)),
        ]
    if cell_type_id:
        cell_type_meta = crud.get_cell_type_meta(db=db, query_list=[cellxgene.CellTypeMeta], filters=[cellxgene.CellTypeMeta.cell_type_id == cell_type_id]).first()
        if cell_type_meta:
            cl_id = cell_type_meta.cell_ontology_id
            filter_list = [cellxgene.CellTaxonomy.specific_cell_ontology_id
                            == cellxgene.CellTaxonomyRelation.cl_id,
                           cellxgene.CellTaxonomy.specific_cell_ontology_id == cl_id]
            public_filter_list = [cellxgene.CellTaxonomy.specific_cell_ontology_id
                                    == cellxgene.CellTaxonomyRelation.cl_id,
                                  cellxgene.CellTaxonomy.specific_cell_ontology_id == cl_id]
    cell_taxonomy_relation_model_list = crud.get_cell_taxonomy_relation_tree(
        db=db, filters=filter_list, public_filter_list=public_filter_list
    )
    res = []
    cell_number_dict, exist_cl_id_list, cl_id_dict = cell_number_util.get_cell_taxonomy_tree_cell_number(db=db)
    for cell_taxonomy_relation_model in cell_taxonomy_relation_model_list:
        res.append(
            {
                "cl_id": cell_taxonomy_relation_model[0],
                "cl_pid": cell_taxonomy_relation_model[2],
                "name": cell_taxonomy_relation_model[1],
                "cell_number": cell_number_dict.get(cell_taxonomy_relation_model[0], 0),
                "is_exist": True if cell_taxonomy_relation_model[0] in exist_cl_id_list else False,
                "cell_type_id": cl_id_dict.get(cell_taxonomy_relation_model[0], "")
            }
        )
    return ResponseMessage(status="0000", data=res, message="ok")


@router.get(
    "/view/table/cell_taxonomy",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
)
async def get_cell_taxonomy_table(
    species_id: int,
    genes_positive: str,
    genes_negative: str,
    order_by: Union[str, None] = None,
    asc: Union[bool, None] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    search_page = page - 1
    res_list = []
    genes_positive_re_match_str = genes_positive.replace(",", "|")
    genes_positive_list = genes_positive.split(",")
    genes_positive_list = [x.upper() for x in genes_positive_list if x != '']
    genes_negative_re_match_str = genes_negative.replace(",", "|")
    filter_list = [cellxgene.CellTypeMeta.species_id == species_id]
    if genes_positive_re_match_str:
        filter_list.append(
            cellxgene.CellTypeMeta.marker_gene_symbol.op("regexp")(
                genes_positive_re_match_str
            )
        )
    if genes_negative_re_match_str:
        filter_list.append(
            cellxgene.CellTypeMeta.marker_gene_symbol.op("not regexp")(
                genes_negative_re_match_str
            )
        )

    cell_type_meta_list = crud.get_cell_type_meta(
        db=db, query_list=[cellxgene.CellTypeMeta], filters=filter_list
    ).all()
    # print(cell_type_meta_list)
    cell_type_id_list = [cell_type_meta.cell_type_id for cell_type_meta in cell_type_meta_list]
    cell_proportion_meta_list = crud.get_cell_proportion_join_project_meta(
        db=db,
        query_list=[cellxgene.CalcCellClusterProportion.cell_type_id, func.sum(cellxgene.CalcCellClusterProportion.cell_number)],
        filters=[cellxgene.CalcCellClusterProportion.cell_type_id.in_(cell_type_id_list)],
        species_id=species_id
    ).group_by(cellxgene.CalcCellClusterProportion.cell_type_id).all()
    cell_proportion_dict = {}
    for cell_proportion_meta in cell_proportion_meta_list:
        cell_proportion_dict[cell_proportion_meta[0]] = cell_proportion_meta[1]
    for cell_type_meta in cell_type_meta_list:
        marker_gene_symbol_list = cell_type_meta.marker_gene_symbol.split(",")
        intersection_list = list(
            set(marker_gene_symbol_list).intersection(set(genes_positive_list))
        )
        cell_type_name = cell_type_meta.cell_type_name
        cell_type_id = cell_type_meta.cell_type_id
        score = len(intersection_list) / len(marker_gene_symbol_list)
        res_list.append(
            {
                "cell_type_id": cell_type_id,
                "cell_type_name": cell_type_name,
                "marker_gene_symbol": cell_type_meta.marker_gene_symbol,
                "intersection_list": intersection_list,
                "score": score,
                "is_exist": True if cell_type_id in cell_proportion_dict.keys() else False,
                "cell_number": cell_proportion_dict.get(cell_type_id, 0)
            }
        )
    if order_by == "score":
        if asc:
            res_list.sort(key=_get_score)
        else:
            res_list.sort(key=_get_score, reverse=True)
    if order_by == "cell_type_id":
        if asc:
            res_list.sort(key=_get_cell_type_id)
        else:
            res_list.sort(key=_get_cell_type_id, reverse=True)
    if order_by == "cell_type_name":
        if asc:
            res_list.sort(key=_get_cell_type_name)
        else:
            res_list.sort(key=_get_cell_type_name, reverse=True)
    if order_by == "cell_number":
        if asc:
            res_list.sort(key=_get_cell_number)
        else:
            res_list.sort(key=_get_cell_number, reverse=True)

    return ResponseMessage(
        status="0000",
        data={
            "list": res_list[search_page * page_size:page * page_size],
            "total": len(res_list),
            "page": page,
            "page_size": page_size,
        },
        message="ok",
    )


def _get_score(cell_type_dict):
    return cell_type_dict.get("score")


def _get_cell_type_id(cell_type_dict):
    return cell_type_dict.get("cell_type_id")


def _get_cell_type_name(cell_type_dict):
    return cell_type_dict.get("cell_type_name")


def _get_cell_number(cell_type_dict):
    return cell_type_dict.get("cell_number")


@router.get(
    "/taxonomy/info",
    response_model=ResponseProjectDetailModel,
    status_code=status.HTTP_200_OK,
)
async def get_cell_taxonomy_info(
    cl_id: str,
    db: Session = Depends(get_db),
    # current_user_email_address = Depends(get_current_user),
) -> ResponseMessage:
    taxonomy_model_list = crud.get_taxonomy(
        db=db, filters=[cellxgene.CellTaxonomy.specific_cell_ontology_id == cl_id]
    ).all()
    # print(taxonomy_model_list)
    return ResponseMessage(status="0000", data=taxonomy_model_list, message="ok")


@router.get("/view/file/{file_type}/{file_id}", status_code=status.HTTP_200_OK)
async def get_csv_data(
    file_type: str,
    file_id: str | None = None,
    group_by: str | None = None,
    # current_user_email_address=Depends(get_current_user),
):
    try:
        if file_id is None:
            return ResponseMessage(status="0201", data={}, message="未上传文件")
        file_path = config.H5AD_FILE_PATH + "/" + file_id
        if file_type == "umap":
            file_data_df = pd.read_csv(file_path)
            fig = px.scatter(file_data_df, x="UMAP_1", y="UMAP_2", color=group_by, width=1280, height=960)
            # fig.show()

            # Save the picture to a byte buffer
            img_byte_arr = fig.to_image(format="png")

            # Return the picture as a response
            try:
                return Response(content=img_byte_arr, media_type="image/png")
            except:
                return ResponseMessage(status="0201", data={}, message="File does not exist")
        elif file_type == "cell_marker":
            try:
                return FileResponse(
                    file_path,
                    media_type="application/octet-stream",
                    filename=file_id,
                )
            except:
                return ResponseMessage(status="0201", data={}, message="File does not exist")
        elif file_type == "pathway_score":
            try:
                return FileResponse(
                    file_path,
                    media_type="application/octet-stream",
                    filename=file_id,
                )
            except:
                return ResponseMessage(status="0201", data={}, message="File does not exist")
    except Exception as e:
        logging.error('[view file error]:{}'.format(str(e)))
        return ResponseMessage(status="0201", data={}, message="failed")


@router.get("/view/file/{file_type}/{file_id}/column", status_code=status.HTTP_200_OK)
async def get_csv_data(
    file_type: str,
    file_id: str | None = None,
    group_by: str | None = None,
    # current_user_email_address=Depends(get_current_user),
):
    try:
        if file_id is None:
            return ResponseMessage(status="0201", data={}, message="Unuploaded file")
        file_path = config.H5AD_FILE_PATH + "/" + file_id
        res_list = []
        if file_type == "umap":
            file_data_df = pd.read_csv(file_path)
            column_list = file_data_df.columns.tolist()
            for i in column_list:
                if "." not in i:
                    res_list.append(i)
            # print(file_data_df.columns.tolist())
        return ResponseMessage(status="0000", data=res_list, message="success")
    except:
        return ResponseMessage(status="0201", data={}, message="failed")


# @router.get("/download/file/meta", status_code=status.HTTP_200_OK)
# async def download_meta_file(
#     current_user_email_address=Depends(get_current_user),
# ):
#     file_path = config.META_FILE_PATH
#     return StreamingResponse(
#         file_util.file_iterator(file_path),
#         media_type="application/octet-stream",
#         headers={"Content-Disposition": f"attachment; filename={file_path}"},
#     )
#
#
# @router.get("/download/file/update_file", status_code=status.HTTP_200_OK)
# async def download_meta_file(
#     current_user_email_address=Depends(get_current_user),
# ):
#     file_path = config.UPDATE_FILE_PATH
#     return StreamingResponse(
#         file_util.file_iterator(file_path),
#         media_type="application/octet-stream",
#         headers={"Content-Disposition": f"attachment; filename={file_path}"},
#     )


# @router.get("/download/file/{file_id}", status_code=status.HTTP_200_OK)
# async def download_file(
#     file_id: str,
#     current_user_email_address=Depends(get_current_user),
# ):
#     file_path = config.H5AD_FILE_PATH + "/" + file_id
#     return StreamingResponse(
#         file_util.file_iterator(file_path),
#         media_type="application/octet-stream",
#         headers={"Content-Disposition": f"attachment; filename={file_path}"},
#     )


@router.get("/download/file/{file_id}", status_code=status.HTTP_200_OK)
async def download_h5ad_file(
    file_id: str,
    download_file_token: str,
    # current_user_email_address=Depends(get_current_user),
):
    can_download, message = auth_util.check_download_file_token(
        download_file_id=file_id, token=download_file_token
    )
    if can_download:
        file_path = config.H5AD_FILE_PATH + "/" + file_id
        return FileResponse(
            path=file_path,
            media_type="application/octet-stream",
            filename=file_id,
        )
    else:
        return ResponseMessage(status="0201", data={}, message=message)


@router.get("/download/file/{file_id}/token", status_code=status.HTTP_200_OK)
async def get_download_h5ad_file_token(
    file_id: str,
    db: Session = Depends(get_db),
    current_user_email_address=Depends(get_current_user),
):
    file_meta = crud.get_file_info(
        db=db, query_list=[cellxgene.FileLibrary], filters=[cellxgene.FileLibrary.file_id == file_id]
    ).first()
    if not file_meta:
        return ResponseMessage(
            status="0201",
            data={},
            message="No corresponding file",
        )
    download_file_token = auth_util.create_download_file_token(file_id, expire_time=120)
    return ResponseMessage(
        status="0000",
        data={
            "download_file_token": download_file_token,
            "file_id": file_id,
        },
        message="success",
    )


@router.get("/view/{analysis_id}", status_code=status.HTTP_200_OK)
async def project_view_h5ad(
    analysis_id: int,
    # url_path: str,
    # request_param: Request,
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
            + "{}/".format(analysis_info.h5ad_id)
            # + "?"
            # + str(request_param.query_params)
        )
    else:
        return ResponseMessage(status="0201", data={}, message="permission denied")
