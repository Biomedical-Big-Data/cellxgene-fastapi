from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from orm.schema import user_model
from orm.db_model import cellxgene

# from orm.dependencies import get_db
from typing import List, AnyStr, Dict


def get_user(db: Session, filters: List):
    return db.query(cellxgene.User).filter(and_(*filters))


def create_user(db: Session, insert_user_model: cellxgene.User):
    db.add(insert_user_model)
    db.commit()


def update_user(db: Session, filters: List, update_dict: Dict):
    db.query(cellxgene.User).filter(and_(*filters)).update(update_dict)
    db.commit()


def create_project(db: Session, insert_project_model: cellxgene.ProjectMeta):
    db.add(insert_project_model)
    db.commit()


def update_project(db: Session, filters: List, update_dict: Dict):
    db.query(cellxgene.ProjectMeta).filter(and_(*filters)).update(update_dict)
    db.commit()


def get_project(db: Session, filters: List):
    return db.query(cellxgene.ProjectMeta).filter(and_(*filters))


def get_project_by_sample(db: Session, filters: List, public_filter_list: List):
    return db.query(cellxgene.BioSampleMeta).filter(
        or_((and_(*filters)), (and_(*public_filter_list)))
    )


def get_project_by_cell(db: Session, filters: List, public_filter_list: List):
    return db.query(cellxgene.CalcCellClusterProportion).filter(
        or_((and_(*filters)), (and_(*public_filter_list)))
    )


def get_project_by_gene(db: Session, filters: List, public_filter_list: List):
    return db.query(cellxgene.CellClusterCellClusterGeneExpressionModel).filter(
        or_((and_(*filters)), (and_(*public_filter_list)))
    )


def get_organ_list(db: Session, filters: List):
    return db.query(cellxgene.BioSampleMeta.organ).filter(and_(*filters))


def get_gene_symbol_list(db: Session, filters: List):
    return db.query(cellxgene.GeneMeta.gene_symbol).filter(and_(*filters))


def get_analysis(db: Session, filters: List):
    return db.query(cellxgene.Analysis).filter(and_(*filters))


def create_analysis(db: Session, insert_analysis_model: cellxgene.Analysis):
    db.add(insert_analysis_model)
    db.flush()
    db.commit()
    return insert_analysis_model.id, insert_analysis_model.project_id


def create_biosample(db: Session, insert_biosample_model: cellxgene.BioSampleMeta):
    db.add(insert_biosample_model)
    db.flush()
    db.commit()
    return insert_biosample_model.id


def update_biosample(db: Session, filters: List, update_dict: Dict):
    db.query(cellxgene.BioSampleMeta).filter(and_(*filters)).update(update_dict)
    db.commit()


def create_project_user(
    db: Session, insert_project_user_model_list: List[cellxgene.ProjectUser]
):
    db.add_all(insert_project_user_model_list)
    # db.commit()


def delete_project_user(db: Session, filters: List):
    db.query(cellxgene.ProjectUser).filter(and_(*filters)).delete()
    # db.commit()


def update_project_for_transaction(db: Session, filters: List, update_dict: Dict):
    db.query(cellxgene.ProjectMeta).filter(and_(*filters)).update(update_dict)


def update_biosample_for_transaction(db: Session, filters: List, update_dict: Dict):
    db.query(cellxgene.BioSampleMeta).filter(and_(*filters)).update(update_dict)


def update_analysis_for_transaction(db: Session, filters: List, update_dict: Dict):
    db.query(cellxgene.Analysis).filter(and_(*filters)).update(update_dict)


def project_update_transaction(
    db: Session,
    delete_project_user_filters: List,
    insert_project_user_model_list: List[cellxgene.ProjectUser],
    update_project_filters: List,
    update_project_dict: Dict,
    update_biosample_filters: List,
    update_biosample_dict: Dict,
    update_analysis_filters: List,
    update_analysis_dict: Dict,
):
    delete_project_user(db=db, filters=delete_project_user_filters)
    create_project_user(
        db=db, insert_project_user_model_list=insert_project_user_model_list
    )
    update_project_for_transaction(
        db=db, filters=update_project_filters, update_dict=update_project_dict
    )
    update_biosample_for_transaction(
        db=db, filters=update_biosample_filters, update_dict=update_biosample_dict
    )
    update_analysis_for_transaction(
        db=db, filters=update_analysis_filters, update_dict=update_analysis_dict
    )
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
    # update_project_biosample_relation(db=next(get_db()))
    # res = get_user(db=next(get_db()), filters=[cellxgene.User.email_address == '619589351@qq.com'])
    # print(res)
    # print(res.first().id)
