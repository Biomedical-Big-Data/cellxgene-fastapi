from fastapi import APIRouter, Depends, HTTPException, status, Header, Body
from fastapi.responses import HTMLResponse
from orm.dependencies import get_db
from orm.schema import user_model
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


@router.get("/list", status_code=status.HTTP_200_OK)
def get_project(search_type: str, filter_list: list, db: Session = Depends(get_db)):
    if search_type == "sample":
        res = crud.get_project_by_sample(db=db, filters=filter_list)
    elif search_type == "cell":
        res = crud.get_project_by_cell(db=db, filters=filter_list)
    elif search_type == "gene":
        res = crud.get_project_by_gene(db=db, filters=filter_list)
    else:
        return ResponseMessage(status='0201', data='wrong type', message='wrong type')
