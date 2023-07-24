from sqlalchemy.orm import Session
from orm.db_model.users import User
from sqlalchemy import and_, or_, func
from orm.schema import user_model


def get_user(db: Session, filters: list):
    return db.query(User).filter(or_(*filters)).first()


def create_user(db: Session, insert_user_model: User):
    db.add(insert_user_model)
    db.commit()


def update_user(db: Session, filters: list, update_dict: dict):
    db.query(User).filter(and_(*filters)).update(update_dict)
    db.commit()
