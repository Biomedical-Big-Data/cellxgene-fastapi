from fastapi import APIRouter, Depends, HTTPException, status, Header, Body
from fastapi.responses import HTMLResponse
from orm.dependencies import get_db
from orm.schema import project_model
from orm.schema.response import ResponseMessage
from orm import crud
from sqlalchemy.orm import Session
from orm.db_model import cellxgene
from utils import auth_util, mail_util
from conf import config


router = APIRouter(
    prefix="/project",
    tags=["project"],
    responses={404: {"description": "Not found"}},
)


@router.get("/list", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def get_project_list(search_type: str, external_project_accesstion: str | None, db: Session = Depends(get_db)):
    filter_list = []
    if search_type == "project":
        filter_list.append(cellxgene.ProjectMeta.external_project_accesstion == external_project_accesstion)
        print(filter_list)
        res = crud.get_project_list(db=db, filters=filter_list)
        return ResponseMessage(status='0201', data='wrong type', message='wrong type')
    return ResponseMessage(status="0000", data="ok", message="ok")
