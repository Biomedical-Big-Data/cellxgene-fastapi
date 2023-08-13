from fastapi import APIRouter, Depends, HTTPException, status, Header, Body, File, UploadFile
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
from io import BytesIO
import pandas as pd


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


@router.get("/list/by/sample", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def get_project_list_by_sample(organ: Union[str, None] = None, species_id: Union[int, None] = None, external_project_accesstion: Union[str, None] = None,
                                      disease: Union[str, None] = None, development_stage: Union[str, None] = None, db: Session = Depends(get_db)):
    filter_list = []
    if organ:
        filter_list.append(cellxgene.BioSampleMeta.organ == organ)
    if species_id:
        filter_list.append(cellxgene.BioSampleMeta.species_id == species_id)
    if external_project_accesstion:
        filter_list.append(cellxgene.BioSampleMeta.external_sample_accesstion == external_project_accesstion)
    if disease:
        filter_list.append(cellxgene.BioSampleMeta.disease.like("%{}%".format(disease)))
    if development_stage:
        filter_list.append(cellxgene.BioSampleMeta.development_stage.like("%{}%".format(development_stage)))
    project_list = crud.get_project_by_sample(db=db, filters=filter_list)
    res_list = []
    for project_biosample in project_list:
        res_dict = {}
        res_dict['title'] = project_biosample[0].title
        res_dict['disease'] = project_biosample[1].disease
        res_dict['sequencing_instrument_manufacturer_model'] = project_biosample[1].sequencing_instrument_manufacturer_model
        res_dict['species'] = project_biosample[1].biosample_species_meta.species
        res_dict['organ'] = project_biosample[1].organ
        res_dict['donor_sex'] = project_biosample[1].biosample_donor_meta.sex
        res_list.append(res_dict)
    print(res_list)
    return ResponseMessage(status="0000", data='ok', message="ok")


@router.post("/upload", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def add_project(file: UploadFile = File()):
    content = await file.read()
    all_sheet_df = pd.read_excel(BytesIO(content), sheet_name=None, dtype=str)
    print(all_sheet_df.keys())
    return ResponseMessage(status="0000", data='ok', message="ok")


@router.post("/update", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def update_project(file: UploadFile = File()):
    content = await file.read()
    all_sheet_df = pd.read_excel(BytesIO(content), sheet_name=None, dtype=str)
    print(all_sheet_df.keys())
    return ResponseMessage(status="0000", data='ok', message="ok")


@router.get("/detail", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def get_project_detail(project_id: int):
    return ResponseMessage(status="0000", data='ok', message="ok")


@router.get("/species/list", response_model=ResponseMessage, status_code=status.HTTP_200_OK)
async def get_species_list(db: Session = Depends(get_db)):
    species_list = crud.get_species_list(db=db, filters=None)
    return ResponseMessage(status="0000", data=species_list, message="ok")