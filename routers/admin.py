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
from utils import auth_util, mail_util, file_util
from conf import config
from typing import List, Union
from io import BytesIO
import pandas as pd
import numpy as np
from orm.dependencies import get_db, get_current_admin
from mqtt_consumer.consumer import SERVER_STATUS_DICT
from uuid import uuid4

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
        return ResponseMessage(status="0201", data={}, message="用户不存在")


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
        return ResponseMessage(status="0201", data={}, message="无更新内容")
    if user_info.email_address:
        check_user_model = crud.get_user(
            db, [cellxgene.User.email_address == user_info.email_address]
        ).first()
        if check_user_model:
            return ResponseMessage(status="0201", data={}, message="此邮箱已有账号")
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
    return ResponseMessage(status="0000", data={}, message="用户信息更新成功")


@router.get(
    "/project/list",
    response_model=ResponseProjectDetailModel,
    status_code=status.HTTP_200_OK,
)
async def get_project_list(
    is_publish: Union[int, None] = None,
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
    "/project/{analysis_id}/file/upload",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
)
async def upload_project_file(
    analysis_id: int,
    project_file: UploadFile = File(...),
    cell_marker_file: UploadFile = File(...),
    umap_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin_email_address=Depends(get_current_admin),
):
    current_user_info = crud.get_user(
        db=db, filters=[cellxgene.User.email_address == current_admin_email_address]
    )
    project_content = await project_file.read()
    project_excel_df = pd.ExcelFile(BytesIO(project_content))
    project_df = project_excel_df.parse("project_meta")
    biosample_df = project_excel_df.parse("biosample_meta")
    cell_proportion_df = project_excel_df.parse("calc_cell_cluster_proportion")
    gene_expression_df = project_excel_df.parse("cell_cluster_gene_expression")
    project_df = project_df.replace(np.nan, None)
    biosample_df = biosample_df.replace(np.nan, None)
    cell_proportion_df = cell_proportion_df.replace(np.nan, None)
    gene_expression_df = gene_expression_df.replace(np.nan, None)
    try:
        cell_marker_file_id = await file_util.save_file(
            db=db,
            file=cell_marker_file,
            insert_user_id=current_user_info.id,
            insert=False,
        )
        umap_file_id = await file_util.save_file(
            db=db, file=umap_file, insert_user_id=current_user_info.id, insert=False
        )
        crud.update_analysis_for_transaction(
            db=db,
            filters=[cellxgene.Analysis.id == analysis_id],
            update_dict={
                "umap_id": umap_file_id,
                "cell_marker_id": cell_marker_file_id,
            },
        )
        update_project_dict = project_df.to_dict("records")[0]
        project_id = update_project_dict.get("id")
        analysis_id_info = crud.get_analysis(
            db=db,
            filters=[
                cellxgene.Analysis.id == analysis_id,
                cellxgene.Analysis.project_id == project_id,
            ],
        ).first()
        if not analysis_id_info:
            return ResponseMessage(
                status="0201", data={}, message="该analysis_id和project_id不存在关联"
            )
        update_project_filter_list = [cellxgene.ProjectMeta.id == project_id]
        crud.update_project_for_transaction(
            db=db, filters=update_project_filter_list, update_dict=update_project_dict
        )
        (
            insert_biosample_model_list,
            check_insert_biosample_id_list,
            update_biosample_id_list,
        ) = ([], [], [])
        insert_project_biosample_model_list, insert_biosample_analysis_model_list = (
            [],
            [],
        )
        (
            insert_cell_proportion_model_list,
            check_insert_cell_proportion_id_list,
        ) = ([], [])
        insert_gene_expression_model_list = []
        for _, row in biosample_df.iterrows():
            biosample_meta = project_model.BiosampleModel(**row.to_dict())
            if type(biosample_meta.id) == str:
                check_insert_biosample_id_list.append(biosample_meta.id)
                insert_biosample_model_list.append(
                    cellxgene.BioSampleMeta(
                        **biosample_meta.model_dump(
                            mode="json", exclude={"id"}, exclude_none=True
                        )
                    )
                )
            else:
                check_biosample_meta = crud.get_biosample(
                    db=db,
                    query_list=[cellxgene.BioSampleMeta],
                    filters=[cellxgene.BioSampleMeta.id == biosample_meta.id],
                )
                if not check_biosample_meta:
                    return ResponseMessage(
                        status="0201", data={}, message="biosample id 不存在"
                    )
                update_biosample_id_list.append(biosample_meta.id)
                crud.update_biosample_for_transaction(
                    db=db,
                    filters=[cellxgene.BioSampleMeta.id == biosample_meta.id],
                    update_dict=biosample_meta.model_dump(
                        mode="json", exclude_none=True
                    ),
                )
        inserted_biosample_id_list = crud.create_biosample_for_transaction(
            db=db, insert_biosample_model_list=insert_biosample_model_list
        )
        inserted_biosample_id_dict = dict(
            zip(check_insert_biosample_id_list, inserted_biosample_id_list)
        )
        inserted_biosample_id_list.extend(update_biosample_id_list)
        for inserted_biosample_id in inserted_biosample_id_list:
            insert_project_biosample_model_list.append(
                cellxgene.ProjectBioSample(
                    project_id=project_id, biosample_id=inserted_biosample_id
                )
            )
            insert_biosample_analysis_model_list.append(
                cellxgene.BioSampleAnalysis(
                    biosample_id=inserted_biosample_id, analysis_id=analysis_id
                )
            )
        crud.delete_project_biosample_for_transaction(
            db=db, filters=[cellxgene.ProjectBioSample.project_id == project_id]
        )
        crud.create_project_biosample_for_transaction(
            db=db,
            insert_project_biosample_model_list=insert_project_biosample_model_list,
        )
        crud.delete_biosample_analysis_for_transaction(
            db=db,
            filters=[
                cellxgene.BioSampleAnalysis.analysis_id == analysis_id,
                cellxgene.ProjectBioSample.project_id == project_id,
                cellxgene.BioSampleAnalysis.biosample_id
                == cellxgene.ProjectBioSample.biosample_id,
            ],
        )
        crud.create_biosample_analysis_for_transaction(
            db=db, insert_biosample_analysis_list=insert_biosample_analysis_model_list
        )
        for _, row in cell_proportion_df.iterrows():
            cell_proportion_meta = project_model.CellClusterProportionModel(
                **row.to_dict()
            )
            cell_proportion_meta.biosample_id = (
                cell_proportion_meta.biosample_id
                if type(cell_proportion_meta.biosample_id) == int
                else int(
                    inserted_biosample_id_dict.get(cell_proportion_meta.biosample_id)
                )
            )
            cell_proportion_meta.analysis_id = analysis_id
            if cell_proportion_meta.biosample_id not in inserted_biosample_id_list:
                return ResponseMessage(
                    status="0201", data={}, message="请选择biosample_meta中存在的biosample_id"
                )
            if type(cell_proportion_meta.calculated_cell_cluster_id) == str:
                check_insert_cell_proportion_id_list.append(
                    cell_proportion_meta.calculated_cell_cluster_id
                )
                insert_cell_proportion_model_list.append(
                    cellxgene.CalcCellClusterProportion(
                        **cell_proportion_meta.model_dump(
                            mode="json",
                            exclude={"calculated_cell_cluster_id"},
                            exclude_none=True,
                        ),
                    ),
                )
            else:
                check_cell_proportion_meta = crud.get_cell_proportion(
                    db=db,
                    filters=[
                        cellxgene.CalcCellClusterProportion.calculated_cell_cluster_id
                        == cell_proportion_meta.calculated_cell_cluster_id
                    ],
                )
                if not check_cell_proportion_meta:
                    return ResponseMessage(
                        status="0201", data={}, message="cell proportion id 不存在"
                    )
                crud.update_cell_proportion_for_transaction(
                    db=db,
                    filters=[
                        cellxgene.CalcCellClusterProportion.calculated_cell_cluster_id
                        == cell_proportion_meta.calculated_cell_cluster_id
                    ],
                    update_dict=cell_proportion_meta.model_dump(
                        mode="json", exclude_none=True
                    ),
                )
        inserted_cell_proportion_id_list = crud.create_cell_proprotion_for_transaction(
            db=db, insert_cell_proportion_model_list=insert_cell_proportion_model_list
        )
        inserted_cell_proportion_id_dict = dict(
            zip(check_insert_cell_proportion_id_list, inserted_cell_proportion_id_list)
        )
        for _, row in gene_expression_df.iterrows():
            gene_expression_meta = project_model.CellClusterGeneExpressionModel(
                **row.to_dict()
            )
            gene_expression_meta.calculated_cell_cluster_id = (
                gene_expression_meta.calculated_cell_cluster_id
                if type(gene_expression_meta.calculated_cell_cluster_id) == int
                else int(
                    inserted_cell_proportion_id_dict.get(
                        gene_expression_meta.calculated_cell_cluster_id
                    )
                )
            )
            if type(gene_expression_meta.id) == str:
                insert_gene_expression_model_list.append(
                    cellxgene.CellClusterGeneExpression(
                        **gene_expression_meta.model_dump(
                            mode="json", exclude={"id"}, exclude_none=True
                        ),
                    )
                )
            else:
                check_gene_expression_meta = crud.get_gene_expression(
                    db=db,
                    filters=[
                        cellxgene.CellClusterGeneExpression.id
                        == gene_expression_meta.id
                    ],
                )
                if not check_gene_expression_meta:
                    return ResponseMessage(
                        status="0201", data={}, message="gene expression id 不存在"
                    )
                crud.update_gene_expression_for_transaction(
                    db=db,
                    filters=[
                        cellxgene.CellClusterGeneExpression.id
                        == gene_expression_meta.id
                    ],
                    update_dict=gene_expression_meta.model_dump(
                        mode="json", exclude_none=True
                    ),
                )
        crud.create_gene_expression_for_transaction(
            db=db,
            insert_gene_expression_model_list=insert_gene_expression_model_list,
        )
    except Exception as e:
        print(e)
        return ResponseMessage(status="0201", data={"error": str(e)}, message="更新失败")
    else:
        db.commit()
        return ResponseMessage(status="0000", data={}, message="更新成功")


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
        return ResponseMessage(status="0201", data={}, message="无此项目")
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
        return ResponseMessage(status="0000", data={}, message="项目状态更新成功")
    except:
        return ResponseMessage(status="0201", data={}, message="项目状态更新失败")


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
    search_page = (page - 1) * page_size
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
        crud.get_project_by_cell(db=db, filters=filter_list, public_filter_list=[])
        .offset(search_page)
        .limit(page_size)
        .all()
    )
    total = crud.get_project_by_cell(
        db=db, filters=filter_list, public_filter_list=[]
    ).count()
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
    search_page = (page - 1) * page_size
    filter_list = []
    if gene_symbol is not None:
        filter_list.append(
            cellxgene.GeneMeta.gene_symbol.like("%{}%".format(gene_symbol))
        )
    if species_id is not None:
        filter_list.append(cellxgene.GeneMeta.species_id == species_id)
    gene_meta_list = (
        crud.get_project_by_gene(
            db=db,
            query_list=[cellxgene.CellClusterGeneExpression],
            filters=filter_list,
            public_filter_list=[],
        )
        .offset(search_page)
        .limit(page_size)
        .all()
    )
    total = crud.get_project_by_gene(
        db=db,
        query_list=[cellxgene.CellClusterGeneExpression],
        filters=filter_list,
        public_filter_list=[],
    ).count()
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
