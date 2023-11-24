import logging
import shutil
import os
import traceback

import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session
from conf import config
from uuid import uuid4
from orm.db_model import cellxgene
from fastapi import UploadFile
from orm import crud
from io import BytesIO
from orm.schema.exception_model import BusinessException
from utils import mail_util

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


async def save_file(
    db: Session, file: UploadFile, insert_user_model: cellxgene.User, insert: bool = True
):
    contents = await file.read()
    filename = file.filename
    filesize = len(contents)
    if insert_user_model.role == config.UserRole.USER_ROLE_FORMAL:
        file_size_meta = crud.get_file_info(db=db,
                                            query_list=[func.sum(cellxgene.FileLibrary.file_size)],
                                            filters=[cellxgene.FileLibrary.upload_user_id == insert_user_model.id,
                                                     cellxgene.FileLibrary.file_status == config.FileStatus.NORMAL]
                                            ).first()
        if not file_size_meta[0]:
            whole_file_size = 0
        else:
            whole_file_size = file_size_meta[0]
        if whole_file_size + filesize >= config.NormalUserLimit.MAXFILESIZE:
            raise BusinessException(message="Common users can only upload a maximum of 10GB files")
    file_name_list = filename.split(".")
    file_name_suffix = file_name_list[len(file_name_list) - 1 :][0]
    file_id = str(uuid4()).replace("-", "") + "." + file_name_suffix
    # print(f"{PROJECT_ROOT}/{config.H5AD_FILE_PATH}/{file_id}")
    try:
        with open(f"{config.H5AD_FILE_PATH}/{file_id}", "wb") as f:
            f.write(contents)
            insert_h5ad_model = cellxgene.FileLibrary(
                file_id=file_id, file_name=filename, upload_user_id=insert_user_model.id, file_size=filesize, file_status=config.FileStatus.NORMAL
            )
            if insert:
                crud.create_file(db=db, insert_file_model=insert_h5ad_model)
            else:
                crud.create_file_for_transaction(db=db, insert_file_model=insert_h5ad_model)
    except Exception as e:
        logging.error("[save file error: {}]".format(str(traceback.format_exc())))
        raise BusinessException(message="upload file failed")
    else:
        return file_id


async def save_meta_file(
    db: Session, file: UploadFile, insert_user_id: int, meta_type: str
):
    contents = await file.read()
    filename = file.filename
    file_name_list = filename.split(".")
    file_name_suffix = file_name_list[len(file_name_list) - 1 :][0]
    file_id = str(uuid4()).replace("-", "") + "." + file_name_suffix
    # print(f"{PROJECT_ROOT}/{config.H5AD_FILE_PATH}/{file_id}")
    with open(f"{config.META_FILE_PATH}/{file_id}", "wb") as f:
        f.write(contents)
        insert_update_meta_file_model = cellxgene.MetaUpdateHistory(
            meta_type=meta_type, file_id=file_id, file_name=filename, upload_user_id=insert_user_id
        )
        crud.create_meta_update_history(db=db, insert_meta_update_history_model=insert_update_meta_file_model)
    return file_id


def file_iterator(file_path, block_size=65536):
    with open(file_path, "rb") as file:
        while True:
            block = file.read(block_size)
            if not block:
                break
            yield block


def copy_file(db: Session, file_ids: str, upload_user_id: int):
    file_id_list = file_ids.split(",")
    return_file_id = ""
    for file_id in file_id_list:
        old_file_path = config.H5AD_FILE_PATH + "/" + file_id
        file_name_list = file_id.split(".")
        file_name_suffix = file_name_list[len(file_name_list) - 1 :][0]
        new_file_id = str(uuid4()).replace("-", "") + "." + file_name_suffix
        file_info = (
            crud.get_file_info(
                db=db, query_list=[cellxgene.FileLibrary], filters=[cellxgene.FileLibrary.file_id == file_id]
            )
            .first()
        )
        insert_h5ad_model = cellxgene.FileLibrary(
            file_id=new_file_id, file_name=file_info.file_name, upload_user_id=upload_user_id, file_size=file_info.file_size, file_status=file_info.file_status
        )
        crud.create_file(db=db, insert_file_model=insert_h5ad_model)
        new_file_path = config.H5AD_FILE_PATH + "/" + new_file_id
        shutil.copy(old_file_path, new_file_path)
        return_file_id = new_file_id + ","
    return return_file_id[:-1]


def update_cell_type_meta_file(db: Session, meta_file: UploadFile, project_content, send_mail_address, upload_user_id):
    project_excel_df = pd.ExcelFile(BytesIO(project_content))
    try:
        crud.delete_cell_type_meta_for_transaction(db=db, filters=[])
        cell_type_meta_df = project_excel_df.parse("cell_type_meta")
        cell_type_meta_df = cell_type_meta_df.fillna("")
        if not cell_type_meta_df.empty:
            insert_cell_type_meta_list = []
            for _, row in cell_type_meta_df.iterrows():
                insert_cell_type_meta_list.append(
                    cellxgene.CellTypeMeta(
                        cell_type_alias_id=row["cell_type_alias_id"]
                        if row["cell_type_alias_id"]
                        else None,
                        species_id=row["species_id"] if row["species_id"] else None,
                        marker_gene_symbol=row["marker_gene_symbol"]
                        if row["marker_gene_symbol"]
                        else None,
                        cell_taxonomy_id=row["cell_taxonomy_id"]
                        if row["cell_taxonomy_id"]
                        else None,
                        cell_taxonomy_url=row["cell_taxonomy_url"]
                        if row["cell_taxonomy_url"]
                        else None,
                        cell_ontology_id=row["cell_ontology_id"]
                        if row["cell_ontology_id"]
                        else None,
                        cell_type_name=row["cell_type_name"]
                        if row["cell_type_name"]
                        else None,
                        cell_type_description=row["cell_type_description"]
                        if row["cell_type_description"]
                        else None,
                        cell_type_ontology_label=row["cell_type_ontology_label"]
                        if row["cell_type_ontology_label"]
                        else None,
                    )
                )
            crud.create_cell_type_meta_for_transaction(
                db=db, insert_cell_type_model_list=insert_cell_type_meta_list
            )
        db.commit()
        mail_util.send_mail(
            mail_template="您上传的Meta信息更新成功",
            subject="Meta信息更新成功",
            to_list=send_mail_address,
        )
    except Exception as e:
        mail_util.send_mail(
            mail_template="您上传的Meta信息更新失败",
            subject="Meta信息更新失败",
            to_list=send_mail_address,
        )
        logging.error("[update_meta_file error]: {}".format(str(e)))
    else:
        save_meta_file(db=db, file=meta_file, insert_user_id=upload_user_id, meta_type="cell_type")


# def update_donor_meta_file(db: Session, project_content, send_mail_address):
#     project_excel_df = pd.ExcelFile(BytesIO(project_content))
#     try:
#         donor_meta_df = project_excel_df.parse("donor_meta")
#         donor_meta_df = donor_meta_df.fillna('')
#         if not donor_meta_df.empty:
#             insert_donor_meta_list = []
#             for _, row in donor_meta_df.iterrows():
#                 insert_donor_meta_list.append(
#                     cellxgene.DonorMeta(
#                         donor_name=row['donor_name'] if row['donor_name'] else None,
#                         sex=row['sex'] if row['sex'] else None,
#                         ethnicity=row['ethnicity'] if row['ethnicity'] else None,
#                         race=row['race'] if row['race'] else None,
#                         mhc_genotype=row['mhc_genotype'] if row['mhc_genotype'] else None,
#                         alcohol_history=row['alcohol_history'] if row['alcohol_history'] else None,
#                         medications=row['medications'] if row['medications'] else None,
#                         nutritional_state=row['nutritional_state'] if row['nutritional_state'] else None,
#                         smoking_history=row['smoking_history'] if row['smoking_history'] else None,
#                         test_results=row['test_results'] if row['test_results'] else None
#                     )
#                 )
#             crud.create_donor_meta(db=db, insert_donor_meta_list=insert_donor_meta_list)
#         mail_util.send_mail(
#             mail_template="您上传的Meta信息更新成功", subject="Meta信息更新成功", to_list=send_mail_address
#         )
#     except Exception as e:
#         mail_util.send_mail(
#             mail_template="您上传的Meta信息更新失败", subject="Meta信息更新失败", to_list=send_mail_address
#         )
#         logging.error('[update_meta_file error]: {}'.format(str(e)))


def update_gene_meta_file(db: Session, meta_file: UploadFile, project_content, send_mail_address, upload_user_id):

    project_excel_df = pd.ExcelFile(BytesIO(project_content))
    try:
        crud.delete_gene_meta_for_transaction(db=db, filters=[])
        gene_meta_df = project_excel_df.parse("gene_meta")
        gene_meta_df = gene_meta_df.fillna("")
        species_meta_list = crud.get_species_list(
            db=db, query_list=[cellxgene.SpeciesMeta], filters=[]
        )
        species_id_dict = {}
        for species_meta in species_meta_list:
            if species_meta.species not in species_id_dict.keys():
                species_id_dict[species_meta.species] = species_meta.id
        if not gene_meta_df.empty:
            insert_gene_model_list = []
            for _, row in gene_meta_df.iterrows():
                insert_gene_model_list.append(
                    cellxgene.GeneMeta(
                        gene_ensemble_id=row["gene_ensemble_id"],
                        species_id=species_id_dict.get(row["species"])
                        if row.get("species")
                        else 1,
                        ortholog=None if not row["ortholog"] else row["ortholog"],
                        gene_symbol=row["gene_symbol"],
                        gene_name=None
                        if row["gene_name"] == "NULL"
                        else row["gene_name"],
                        alias=None if row["alias"] == "NULL" else row["alias"],
                        gene_ontology=None if row["alias"] == "NULL" else row["alias"],
                        gpcr=None if row["gpcr"] == "NULL" else row["gpcr"],
                        tf=None if row["tf"] == "NULL" else row["tf"],
                        surfaceome=None
                        if row["surfaceome"] == "NULL"
                        else row["surfaceome"],
                        drugbank_drugtarget=None
                        if row["drugbank_drugtarget"] == "NULL"
                        else row["drugbank_drugtarget"],
                        phenotype=None
                        if row["phenotype"] == "NULL"
                        else row["phenotype"],
                    )
                )
            crud.create_gene_for_transaction(db=db, insert_gene_model_list=insert_gene_model_list)
        db.commit()
        mail_util.send_mail(
            mail_template="您上传的Meta信息更新成功",
            subject="Meta信息更新成功",
            to_list=send_mail_address,
        )
    except Exception as e:
        mail_util.send_mail(
            mail_template="您上传的Meta信息更新失败",
            subject="Meta信息更新失败",
            to_list=send_mail_address,
        )
        logging.error("[update_meta_file error]: {}".format(str(e)))
    else:
        save_meta_file(db=db, file=meta_file, insert_user_id=upload_user_id, meta_type="gene")


def update_species_meta_file(db: Session, meta_file: UploadFile, project_content, send_mail_address, upload_user_id):

    project_excel_df = pd.ExcelFile(BytesIO(project_content))
    try:
        crud.delete_species_meta_for_transaction(db=db, filters=[])
        species_meta_df = project_excel_df.parse("species_meta")
        species_meta_df = species_meta_df.fillna("")
        if not species_meta_df.empty:
            insert_species_meta_list = []
            for _, row in species_meta_df.iterrows():
                insert_species_meta_list.append(
                    cellxgene.SpeciesMeta(
                        species=row["species"],
                        species_ontology_label=row["species_ontology_label"],
                    )
                )
            crud.create_species_for_transaction(
                db=db, insert_species_model_list=insert_species_meta_list
            )
        db.commit()
        mail_util.send_mail(
            mail_template="您上传的Meta信息更新成功",
            subject="Meta信息更新成功",
            to_list=send_mail_address,
        )
    except Exception as e:
        mail_util.send_mail(
            mail_template="您上传的Meta信息更新失败",
            subject="Meta信息更新失败",
            to_list=send_mail_address,
        )
        logging.error("[update_meta_file error]: {}".format(str(e)))
    else:
        save_meta_file(db=db, file=meta_file, insert_user_id=upload_user_id, meta_type="species")


def remove_file(file_id: str):
    file_path = config.H5AD_FILE_PATH + "/" + file_id
    os.unlink(file_path)


if __name__ == "__main__":
    pass
    # remove_file("4aa46073190944b2a965c0f0ca53ca6a.mov")
    # from orm.dependencies import get_db
    # file_id = copy_file(db=next(get_db()), file_id='918e8def0a074ec2ad8270261003ce45.h5ad', upload_user_id=25)
    # print(file_id)
