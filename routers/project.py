from fastapi import APIRouter, Depends, HTTPException, status, Header, Body
from fastapi.responses import HTMLResponse
from orm.dependencies import get_db
from orm.schema import project_model
from orm.schema.response import ResponseMessage
from orm import crud
from sqlalchemy.orm import Session
from orm.db_model import cellxgene
from orm.schema.project_model import ResponseProjectModel
from utils import auth_util, mail_util
from conf import config
from typing import List, Union


router = APIRouter(
    prefix="/project",
    tags=["project"],
    responses={404: {"description": "Not found"}},
)


@router.get("/list", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def get_project_list(search_type: str, external_project_accesstion: Union[str, None] = None, disease:  Union[str, None] = None, db: Session = Depends(get_db)):
    filter_list = []
    if search_type == "project":
        filter_list.append(cellxgene.ProjectMeta.external_project_accesstion == external_project_accesstion)
        res = crud.get_project_list(db=db, filters=filter_list)
        for i in res:
            print(i[0].title, i[1].bmi)
    elif search_type == "sample":
        filter_list.append(cellxgene.BioSampleMeta.disease == disease)
        res = crud.get_project_list(db=db, filters=filter_list)
        for i in res:
            print(i[0].title, i[1].bmi)
    return ResponseMessage(status="0000", data="ok", message="ok")
