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
    return db.query(cellxgene.ProjectMeta, cellxgene.BioSampleMeta).filter(and_(*filters)).offset(skip).limit(limit).all()


def get_project_by_cell(db: Session, filters: List, skip: int = 0, limit: int = 20):
    return db.query(cellxgene.ProjectMeta).filter(and_(*filters)).offset(skip).limit(limit).all()


def get_project_by_gene(db: Session, filters: List, skip: int = 0, limit: int = 20):
    db.query(cellxgene.ProjectMeta).filter(and_(*filters)).offset(skip).limit(limit).all()


def create_project_biosample(db: Session):
    project_meta = cellxgene.ProjectMeta(integrated_project=0, title='ghjfgdh', external_project_accesstion='ioyuiu')
    biosample_meta = cellxgene.BioSampleMeta(external_sample_accesstion='asdasd', species_id=1, donor_id=1, bmi=30, disease='4656745')
    biosample_meta2 = cellxgene.BioSampleMeta(external_sample_accesstion='iiiii', species_id=1, donor_id=1, bmi=55,
                                             disease='dedad')
    project_meta.project_biosample_meta.append(biosample_meta)
    project_meta.project_biosample_meta.append(biosample_meta2)
    db.add(project_meta)
    db.commit()


def update_project_biosample(db: Session):
    db.query(cellxgene.ProjectMeta).filter(cellxgene.ProjectMeta.id == 1).update({"id":3})
    db.commit()


def delete_project_biosample(db: Session):
    db.query(cellxgene.ProjectMeta).filter(cellxgene.ProjectMeta.id == 2).delete()
    db.commit()


def add_project_biosample_relation(db: Session):
    project_meta = db.query(cellxgene.ProjectMeta).filter(cellxgene.ProjectMeta.id == 1).first()
    biosample_meta_list = db.query(cellxgene.BioSampleMeta).filter(cellxgene.BioSampleMeta.id.in_([2, 6, 7])).all()
    print(project_meta)
    print(biosample_meta_list)
    for i in biosample_meta_list:
        project_meta.project_biosample_meta.append(i)
    db.commit()


def update_project_biosample_relation(db: Session):
    project_meta = db.query(cellxgene.ProjectMeta).filter(cellxgene.ProjectMeta.id == 5).first()
    biosample_meta_list = db.query(cellxgene.BioSampleMeta).filter(cellxgene.BioSampleMeta.id.in_([11,13])).all()
    biosample_meta2 = cellxgene.BioSampleMeta(external_sample_accesstion='rewrtrt', species_id=1, donor_id=1, bmi=1,
                                              disease='head')
    biosample_meta_list.append(biosample_meta2)
    print(project_meta)
    print(biosample_meta_list)
    # for i in biosample_meta_list:
    project_meta.project_biosample_meta = biosample_meta_list
    db.commit()


def delete_project_biosample_relation(db: Session):
    project_meta = db.query(cellxgene.ProjectMeta).filter(cellxgene.ProjectMeta.id == 1).first()
    biosample_meta_list = db.query(cellxgene.BioSampleMeta).filter(cellxgene.BioSampleMeta.id.in_([6, 7])).all()
    for i in biosample_meta_list:
        project_meta.project_biosample_meta.remove(i)
    db.commit()


def clear_project_biosample_relation(db: Session):
    project_meta = db.query(cellxgene.ProjectMeta).filter(cellxgene.ProjectMeta.id == 1).first()
    project_meta.project_biosample_meta.clear()
    db.commit()


def get_species_list(db: Session, filters: List | None):
    return db.query(cellxgene.SpeciesMeta).filter(and_(*filters)).all()


if __name__ == "__main__":
    pass
    # create_project_biosample(db=next(get_db()))
    # update_project_biosample(db=next(get_db()))
    # delete_project_biosample(db=next(get_db()))
    # add_project_biosample_relation(db=next(get_db()))
    # delete_project_biosample_relation(db=next(get_db()))
    update_project_biosample_relation(db=next(get_db()))