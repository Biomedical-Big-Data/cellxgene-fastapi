from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from orm.schema import user_model
from orm.db_model import cellxgene
from orm.dependencies import get_db


def get_user(db: Session, filters: list):
    return db.query(cellxgene.User).filter(or_(*filters)).first()


def create_user(db: Session, insert_user_model: cellxgene.User):
    db.add(insert_user_model)
    db.commit()


def update_user(db: Session, filters: list, update_dict: dict):
    db.query(cellxgene.User).filter(and_(*filters)).update(update_dict)
    db.commit()


def get_project(db: Session, filters: list, skip: int = 0, limit: int = 20):
    db.query(cellxgene.Project).filter(and_(*filters)).offset(skip).limit(limit).all()


def get_sample(db: Session, filters: list, skip: int = 0, limit: int = 20):
    db.query(cellxgene.BioSample).filter(and_(*filters)).offset(skip).limit(limit).all()


def get_sample_donor_message(db: Session, bio_id):
    return db.query(cellxgene.BioSample).filter(cellxgene.BioSample.id == bio_id).first()


if __name__ == "__main__":
    bio_msg = get_sample_donor_message(db=next(get_db()), bio_id=1)
    print(bio_msg.donor_msg.sex)