import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Header,
    Body,
    File,
    UploadFile,
    BackgroundTasks,
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
from utils import auth_util, mail_util, file_util, upload_excel_util
from conf import config
from typing import List, Union
from orm.dependencies import get_db, get_current_admin
from mqtt_consumer.consumer import SERVER_STATUS_DICT
from uuid import uuid4

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={200: {"description": {"status": "0000", "data": {}, "message": "failed"}}},
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
    search_page = (page - 1) * page_size
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
        return ResponseMessage(status="0201", data={}, message="User does not exist")


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
        return ResponseMessage(status="0201", data={}, message="No updated content")
    if user_info.email_address:
        check_user_model = crud.get_user(
            db, [cellxgene.User.email_address == user_info.email_address]
        ).first()
        if check_user_model:
            return ResponseMessage(status="0201", data={}, message="This email already has an account")
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
    return ResponseMessage(status="0000", data={}, message="The user information is updated successful")


@router.get(
    "/project/list",
    response_model=ResponseProjectDetailModel,
    status_code=status.HTTP_200_OK,
)
async def get_project_list(
    is_publish: Union[int, None] = None,
    is_private: Union[int, None] = None,
    title: Union[str, None] = None,
    create_at: Union[str, None] = None,
    page: int = 1,
    page_size: int = 20,
    asc: int = 1,
    db: Session = Depends(get_db),
    current_admin_email_address=Depends(get_current_admin),
) -> ResponseMessage:
    search_page = (page - 1) * page_size
    filter_list = []
    if is_publish is not None:
        filter_list.append(cellxgene.ProjectMeta.is_publish == is_publish)
    if is_private is not None:
        filter_list.append(cellxgene.ProjectMeta.is_private == is_private)
    if title is not None:
        filter_list.append(cellxgene.ProjectMeta.title.like("%{}%".format(title)))
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


@router.post(
    "/project/{project_id}/update",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
)
async def admin_update_project(
    background_tasks: BackgroundTasks,
    project_id: int,
    admin_update_model: project_model.AdminUpdateProjectModel,
    db: Session = Depends(get_db),
    current_admin_email_address=Depends(get_current_admin),
):
    filter_list = [cellxgene.ProjectMeta.id == project_id]
    try:
        project_info = crud.get_project(db=db, filters=filter_list).first()
        analysis_info = crud.get_analysis(db=db, filters=[cellxgene.Analysis.id == admin_update_model.analysis_id]).first()
        if not project_info:
            return ResponseMessage(status="0201", data={}, message="Project does not exist")
        update_project_dict = {
            "title": admin_update_model.title,
            "description": admin_update_model.description,
            "tags": admin_update_model.tags,
            "is_publish": admin_update_model.is_publish if admin_update_model.is_publish else project_info.is_publish,
            "is_private": admin_update_model.is_private,
        }
        member_info_list = crud.get_user(
            db=db, filters=[cellxgene.User.email_address.in_(admin_update_model.members)]
        ).all()
        insert_project_user_model_list = []
        for member_info in member_info_list:
            insert_project_user_model_list.append(
                cellxgene.ProjectUser(project_id=project_id, user_id=member_info.id)
            )
        update_analysis_id = project_info.project_analysis_meta[0].id
        # h5ad_id = str(uuid4()).replace("-", "")
        update_analysis_dict = {
            "h5ad_id": admin_update_model.h5ad_id
            if admin_update_model.h5ad_id
            else project_info.project_analysis_meta[0].h5ad_id,
            "cell_marker_id": admin_update_model.cell_marker_id
            if admin_update_model.cell_marker_id
            else project_info.project_analysis_meta[0].cell_marker_id,
            "umap_id": admin_update_model.umap_id
            if admin_update_model.umap_id
            else project_info.project_analysis_meta[0].umap_id,
        }
        crud.admin_project_update_transaction(
            db=db,
            delete_project_user_filters=[
                cellxgene.ProjectUser.project_id == project_id
            ],
            insert_project_user_model_list=insert_project_user_model_list,
            update_project_filters=[cellxgene.ProjectMeta.id == project_id],
            update_project_dict=update_project_dict,
            update_analysis_filters=[cellxgene.Analysis.id == update_analysis_id],
            update_analysis_dict=update_analysis_dict,
        )
        if admin_update_model.excel_id is not None and admin_update_model.excel_id != analysis_info.excel_id:
            background_tasks.add_task(
                upload_excel_util.upload_file_v2,
                db,
                project_id,
                admin_update_model.analysis_id,
                admin_update_model.excel_id,
                current_admin_email_address,
            )
    except Exception as e:
        print(e)
        return ResponseMessage(status="0201", data={"error": str(e)}, message="Update failed")
    else:
        return ResponseMessage(status="0000", data={}, message="Update success, project file update results please wait for email reply")


@router.post(
    "/project/{project_id}/transfer",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
)
async def transfer_project(
    project_id: int,
    transfer_to: project_model.TransferProjectModel = Body(),
    db: Session = Depends(get_db),
    current_admin_email_address=Depends(get_current_admin),
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
        return ResponseMessage(status="0201", data={}, message="Project does not exist")
    return ResponseMessage(status="0000", data=project_info_model, message="ok")


@router.post(
    "/project/{project_id}/status/update",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
)
async def update_project(
    project_id: int,
    update_project_model: project_model.UpdateProjectModel = Body(),
    db: Session = Depends(get_db),
    current_admin_email_address=Depends(get_current_admin),
):
    try:
        crud.update_project(
            db=db,
            filters=[cellxgene.ProjectMeta.id == project_id],
            update_dict={"is_publish": update_project_model.is_publish},
        )
        return ResponseMessage(status="0000", data={}, message="The project status update succeeded")
    except:
        return ResponseMessage(status="0201", data={}, message="Project status update failed")


@router.post(
    "/project/{project_id}/offline",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
)
async def update_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_admin_email_address=Depends(get_current_admin),
):
    try:
        crud.update_project(
            db=db,
            filters=[cellxgene.ProjectMeta.id == project_id],
            update_dict={"is_publish": config.ProjectStatus.PROJECT_STATUS_DRAFT},
        )
        return ResponseMessage(status="0000", data={}, message="Project offline successful")
    except:
        return ResponseMessage(status="0201", data={}, message="Project offline failed")


@router.post(
    "/cell_type_meta/create",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK
)
async def create_cell_type_meta(
    create_cell_type_model: project_model.CreateCellTypeModel = Body(),
    db: Session = Depends(get_db),
    # current_admin_email_address=Depends(get_current_admin),
):
    cell_type_id = create_cell_type_model.cell_type_id
    species_id = create_cell_type_model.species_id
    exist_cell_type_meta = crud.get_cell_type_meta(db=db, query_list=[cellxgene.CellTypeMeta], filters=[cellxgene.CellTypeMeta.cell_type_id == cell_type_id,
                                                                                                        cellxgene.CellTypeMeta.species_id == species_id]).first()
    if not exist_cell_type_meta:
        crud.create_cell_type_meta(db=db, insert_cell_type_model_list=[cellxgene.CellTypeMeta(**create_cell_type_model.model_dump(
                        mode="json"
                    ),)])
        return ResponseMessage(status="0000", data={}, message="Cell_type create success")
    else:
        return ResponseMessage(status="0201", data={}, message="Cell_type is already exist")


@router.get(
    "/cell/list",
    response_model=ResponseProjectListModel,
    status_code=status.HTTP_200_OK,
)
async def get_cell_list(
    cell_type_name: Union[str, None] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_admin_email_address=Depends(get_current_admin),
):
    filter_list = []
    search_page = (page - 1) * page_size
    if cell_type_name is not None:
        filter_list.append(
            cellxgene.CellTypeMeta.cell_type_name.like("%{}%".format(cell_type_name))
        )
    cell_type_list = (
        crud.get_cell_type_meta(
            db=db, query_list=[cellxgene.CellTypeMeta], filters=filter_list
        )
        .offset(search_page)
        .limit(page_size)
        .all()
    )
    total = crud.get_cell_type_meta(
        db=db, query_list=[cellxgene.CellTypeMeta], filters=filter_list
    ).count()
    res_dict = {
        "cell_type_list": cell_type_list,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    return ResponseMessage(status="0000", data=res_dict, message="ok")


@router.get(
    "/donor/list",
    response_model=ResponseProjectListModel,
    status_code=status.HTTP_200_OK,
)
async def get_donor_list(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_admin_email_address=Depends(get_current_admin),
):
    filter_list = []
    search_page = (page - 1) * page_size
    donor_meta_list = (
        crud.get_donor_meta(db=db, filters=filter_list)
        .offset(search_page)
        .limit(page_size)
        .all()
    )
    total = crud.get_donor_meta(db=db, filters=filter_list).count()
    res_dict = {
        "donor_list": donor_meta_list,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    return ResponseMessage(status="0000", data=res_dict, message="ok")


@router.get(
    "/species/list",
    response_model=ResponseProjectListModel,
    status_code=status.HTTP_200_OK,
)
async def get_species_list(
    species: Union[str, None] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_admin_email_address=Depends(get_current_admin),
):
    filter_list = []
    search_page = (page - 1) * page_size
    if species is not None:
        filter_list.append(cellxgene.SpeciesMeta.species.like("%{}%".format(species)))
    species_meta_list = (
        crud.get_species_list(
            db=db, query_list=[cellxgene.SpeciesMeta], filters=filter_list
        )
        .offset(search_page)
        .limit(page_size)
        .all()
    )
    total = crud.get_species_list(
        db=db, query_list=[cellxgene.SpeciesMeta], filters=filter_list
    ).count()
    res_dict = {
        "species_list": species_meta_list,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    return ResponseMessage(status="0000", data=res_dict, message="ok")


@router.get(
    "/gene/list",
    response_model=ResponseProjectListModel,
    status_code=status.HTTP_200_OK,
)
async def get_gene_list(
    gene_symbol: Union[str, None] = None,
    gene_name: Union[str, None] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_admin_email_address=Depends(get_current_admin),
) -> ResponseMessage:
    search_page = (page - 1) * page_size
    filter_list = []
    if gene_symbol is not None:
        filter_list.append(
            cellxgene.GeneMeta.gene_symbol.like("%{}%".format(gene_symbol))
        )
    if gene_name is not None:
        filter_list.append(cellxgene.GeneMeta.gene_name.like("%{}%".format(gene_name)))
    gene_meta_list = (
        crud.get_gene_meta(
            db=db,
            filters=filter_list,
        )
        .offset(search_page)
        .limit(page_size)
        .all()
    )
    total = crud.get_gene_meta(
        db=db,
        filters=filter_list,
    ).count()
    res_dict = {
        "gene_list": gene_meta_list,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    return ResponseMessage(status="0000", data=res_dict, message="ok")


@router.get("/project/process/cache_status", status_code=status.HTTP_200_OK)
async def get_project_cache_status(
    current_admin_email_address=Depends(get_current_admin),
):
    return RedirectResponse(config.CELLXGENE_GATEWAY_URL + "/cache_status")


@router.get("/project/process/{h5ad_id}/terminate", status_code=status.HTTP_200_OK)
async def terminate_project_process(
    h5ad_id: str,
    current_admin_email_address=Depends(get_current_admin),
):
    return RedirectResponse(
        config.CELLXGENE_GATEWAY_URL
        + "/terminate/{}".format(h5ad_id)
        + "?source_name=local"
    )


@router.get(
    "/server/status", response_model=ResponseMessage, status_code=status.HTTP_200_OK
)
async def get_server_status(
    current_admin_email_address=Depends(get_current_admin),
):
    server_status_list = [value for key, value in SERVER_STATUS_DICT.items()]
    return ResponseMessage(status="0000", data=server_status_list, message="ok")


@router.post(
    "/project/meta/file/upload",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
)
async def upload_project_meta_file(
    background_tasks: BackgroundTasks,
    file_type: str = Body(),
    meta_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin_email_address=Depends(get_current_admin),
):
    try:
        current_user_info = crud.get_user(
            db=db, filters=[cellxgene.User.email_address == current_admin_email_address]
        ).first()
        project_content = await meta_file.read()
        if file_type == "cell_type":
            background_tasks.add_task(
                file_util.update_cell_type_meta_file,
                db,
                meta_file,
                project_content,
                current_admin_email_address,
                current_user_info.id
            )
        elif file_type == "gene":
            background_tasks.add_task(
                file_util.update_gene_meta_file,
                db,
                meta_file,
                project_content,
                current_admin_email_address,
                current_user_info.id
            )
        # if file_type == "donor":
        #     background_tasks.add_task(
        #         file_util.update_donor_meta_file,
        #         db,
        #         project_content,
        #         current_admin_email_address,
        #     )
        if file_type == "species":
            background_tasks.add_task(
                file_util.update_species_meta_file,
                db,
                meta_file,
                project_content,
                current_admin_email_address,
                current_user_info.id
            )
    except Exception as e:
        logging.error("[upload project meta error]: {}".format(str(e)))
    else:
        return ResponseMessage(status="0000", data={}, message="The file is uploaded successfully. Please wait for the email to receive the data update result")
