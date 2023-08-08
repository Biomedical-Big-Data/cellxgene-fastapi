from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from orm.schema import user_model
from orm.db_model import cellxgene
from orm.dependencies import get_db
from typing import List, AnyStr, Dict


def get_user(db: Session, filters: List):
    return db.query(cellxgene.User).filter(or_(*filters)).first()


def create_user(db: Session, insert_user_model: cellxgene.User):
    db.add(insert_user_model)
    db.commit()


def update_user(db: Session, filters: List, update_dict: Dict):
    db.query(cellxgene.User).filter(and_(*filters)).update(update_dict)
    db.commit()


def get_project_list(db: Session, filters: List, skip: int = 0, limit: int = 20):
    return db.query(cellxgene.ProjectMeta, cellxgene.BioSampleMeta).filter(and_(*filters)).offset(skip).limit(limit).all()


def get_project_by_sample(db: Session, filters: List, skip: int = 0, limit: int = 20):
    return db.query(cellxgene.ProjectMeta).filter(and_(*filters)).offset(skip).limit(limit).all()


def get_project_by_cell(db: Session, filters: List, skip: int = 0, limit: int = 20):
    return db.query(cellxgene.ProjectMeta).filter(and_(*filters)).offset(skip).limit(limit).all()


def get_project_by_gene(db: Session, filters: List, skip: int = 0, limit: int = 20):
    db.query(cellxgene.ProjectMeta).filter(and_(*filters)).offset(skip).limit(limit).all()


def create_project_biosample(db: Session):
    project_meta = cellxgene.ProjectMeta(integrated_project=0, title='test', external_project_accesstion='4444')
    biosample_meta = cellxgene.BioSampleMeta(external_sample_accesstion='4444', species_id=1, donor_id=1, bmi=30, disease='test')
    project_meta.project_biosample_meta.append(biosample_meta)
    db.add(project_meta)
    db.commit()


if __name__ == "__main__":
    pass
    create_project_biosample(db=next(get_db()))