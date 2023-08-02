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
async def get_project_list(search_model: project_model.SearchProjectModel, db: Session = Depends(get_db)):
    filter_list = []
    if search_model.search_type == "sample":
        if search_model.organ:
            filter_list.append(cellxgene.BioSample.organ == search_model.organ)
        if search_model.species_id:
            filter_list.append(cellxgene.BioSample.species_id == search_model.species_id)
        res = crud.get_project_by_sample(db=db, filters=filter_list)
    elif search_model.search_type == "cell":
        if search_model.cell_id:
            filter_list.append(cellxgene.CalcCellClusterProportion.calculated_cell_cluster_id == search_model.cell_id)
        res = crud.get_project_by_cell(db=db, filters=filter_list)
    elif search_model.search_type == "gene":
        if search_model.gene_symbol:
            filter_list.append(cellxgene.Gene.gene_symbol == search_model.gene_symbol)
        res = crud.get_project_by_gene(db=db, filters=filter_list)
    else:
        return ResponseMessage(status='0201', data='wrong type', message='wrong type')
    return ResponseMessage(status="0000", data="ok", message="ok")
