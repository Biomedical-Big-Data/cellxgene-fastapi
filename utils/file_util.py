from sqlalchemy.orm import Session
from conf import config
from uuid import uuid4
from orm.db_model import cellxgene
from fastapi import UploadFile
from orm import crud
import os


PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


async def save_file(
    db: Session, file: UploadFile, insert_user_id: int, insert: bool = True
):
    contents = await file.read()
    filename = file.filename
    file_name_list = filename.split(".")
    file_name_suffix = file_name_list[len(file_name_list) - 1 :][0]
    file_id = str(uuid4()).replace("-", "") + "." + file_name_suffix
    # print(f"{PROJECT_ROOT}/{config.H5AD_FILE_PATH}/{file_id}")
    with open(f"{config.H5AD_FILE_PATH}/{file_id}", "wb") as f:
        f.write(contents)
        insert_h5ad_model = cellxgene.FileLibrary(
            file_id=file_id, file_name=filename, upload_user_id=insert_user_id
        )
        if insert:
            crud.create_h5ad(db=db, insert_h5ad_model=insert_h5ad_model)
        else:
            crud.create_h5ad_for_transaction(db=db, insert_h5ad_model=insert_h5ad_model)
    return file_id
