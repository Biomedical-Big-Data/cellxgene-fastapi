from sqlalchemy.orm import Session
from orm.db_model.users import User
from sqlalchemy import and_, or_, func
from orm.schema import user_model


def get_user(db: Session, filters: list):
    return (
        db.query(User)
        .filter(
            or_(
                *filters
            )
        )
        .first()
    )


def create_user(db: Session, user_name: str, user_password: str):
    pass
