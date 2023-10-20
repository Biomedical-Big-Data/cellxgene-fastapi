import shutil

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
            crud.create_file(db=db, insert_file_model=insert_h5ad_model)
        else:
            crud.create_file_for_transaction(db=db, insert_file_model=insert_h5ad_model)
    return file_id


def file_iterator(file_path, block_size=65536):
    with open(file_path, "rb") as file:
        while True:
            block = file.read(block_size)
            if not block:
                break
            yield block


def copy_file(db: Session, file_ids: str, upload_user_id: int):
    file_id_list = file_ids.split(',')
    return_file_id = ''
    for file_id in file_id_list:
        old_file_path = config.H5AD_FILE_PATH + "/" + file_id
        file_name_list = file_id.split(".")
        file_name_suffix = file_name_list[len(file_name_list) - 1:][0]
        new_file_id = str(uuid4()).replace("-", "") + "." + file_name_suffix
        file_name = crud.get_file_info(db=db, filters=[cellxgene.FileLibrary.file_id == file_id]).first().file_name
        insert_h5ad_model = cellxgene.FileLibrary(
            file_id=new_file_id, file_name=file_name, upload_user_id=upload_user_id
        )
        crud.create_file(db=db, insert_file_model=insert_h5ad_model)
        new_file_path = config.H5AD_FILE_PATH + "/" + new_file_id
        shutil.copy(old_file_path, new_file_path)
        return_file_id = new_file_id + ","
    return return_file_id[:-1]


if __name__ == "__main__":
    pass
    # from orm.dependencies import get_db
    # file_id = copy_file(db=next(get_db()), file_id='918e8def0a074ec2ad8270261003ce45.h5ad', upload_user_id=25)
    # print(file_id)
