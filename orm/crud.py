from sqlalchemy.orm import Session, aliased
from sqlalchemy import and_, or_, func, literal
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


def create_project_user(db: Session, insert_project_user_model: cellxgene.ProjectUser):
    db.add(insert_project_user_model)
    db.commit()


def get_project_by_sample(db: Session, public_filter_list: List):
    return db.query(cellxgene.BioSampleMeta).filter(
        and_(*public_filter_list)
    )
    # return db.query(cellxgene.BioSampleMeta).filter(
    #     or_((and_(*filters)), (and_(*public_filter_list)))
    # )


def get_project_by_cell(db: Session, public_filter_list: List):
    return db.query(cellxgene.CalcCellClusterProportion).filter(
        and_(*public_filter_list)
    )
    # return db.query(cellxgene.CalcCellClusterProportion).filter(
    #     or_((and_(*filters)), (and_(*public_filter_list)))
    # )


def get_project_by_gene(
    db: Session, query_list: List, public_filter_list: List
):
    return db.query(*query_list).filter(
        and_(*public_filter_list)
    )
    # return db.query(*query_list).filter(
    #     or_((and_(*filters)), (and_(*public_filter_list)))
    # )


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


def get_biosample(db: Session, query_list: List, filters: List):
    return db.query(*query_list).filter(and_(*filters))


def update_biosample(db: Session, filters: List, update_dict: Dict):
    db.query(cellxgene.BioSampleMeta).filter(and_(*filters)).update(update_dict)
    db.commit()


def create_cell_proprotion_for_transaction(
    db: Session,
    insert_cell_proportion_model_list: List[cellxgene.CalcCellClusterProportion],
):
    inserted_id_list = []
    for insert_cell_proportion_model in insert_cell_proportion_model_list:
        db.add(insert_cell_proportion_model)
        db.flush()
        inserted_id_list.append(insert_cell_proportion_model.calculated_cell_cluster_id)
    return inserted_id_list


def get_cell_proportion(db: Session, filters: List):
    return db.query(cellxgene.CalcCellClusterProportion).filter(and_(*filters))


def update_cell_proportion_for_transaction(
    db: Session, filters: List, update_dict: Dict
):
    db.query(cellxgene.CalcCellClusterProportion).filter(and_(*filters)).update(
        update_dict
    )


def get_gene_expression(db: Session, filters: List):
    return db.query(cellxgene.CellClusterGeneExpression).filter(and_(*filters))


def update_gene_expression_for_transaction(
    db: Session, filters: List, update_dict: Dict
):
    db.query(cellxgene.CellClusterGeneExpression).filter(and_(*filters)).update(
        update_dict
    )


def create_gene_expression_for_transaction(
    db: Session,
    insert_gene_expression_model_list: List[cellxgene.CellClusterGeneExpression],
):
    db.add_all(insert_gene_expression_model_list)


def get_project_biosample(db: Session, filters: List):
    return db.query(cellxgene.ProjectBioSample).filter(and_(*filters))


def create_project_biosample_for_transaction(
    db: Session, insert_project_biosample_model_list: List[cellxgene.ProjectBioSample]
):
    db.add_all(insert_project_biosample_model_list)


def delete_project_biosample_for_transaction(db: Session, filters: List):
    db.query(cellxgene.ProjectBioSample).filter(and_(*filters)).delete()


def create_biosample_analysis_for_transaction(
    db: Session, insert_biosample_analysis_list: List[cellxgene.BioSampleAnalysis]
):
    db.add_all(insert_biosample_analysis_list)


def delete_biosample_analysis_for_transaction(db: Session, filters: List):
    db.query(cellxgene.BioSampleAnalysis).filter(and_(*filters)).delete()


def create_project_user_for_transaction(
    db: Session, insert_project_user_model_list: List[cellxgene.ProjectUser]
):
    db.add_all(insert_project_user_model_list)


def delete_project_user_for_transaction(db: Session, filters: List):
    db.query(cellxgene.ProjectUser).filter(and_(*filters)).delete()


def update_project_for_transaction(db: Session, filters: List, update_dict: Dict):
    db.query(cellxgene.ProjectMeta).filter(and_(*filters)).update(update_dict)


def create_biosample_for_transaction(
    db: Session, insert_biosample_model_list=List[cellxgene.BioSampleMeta]
):
    inserted_id_list = []
    for insert_biosample_model in insert_biosample_model_list:
        db.add(insert_biosample_model)
        db.flush()
        inserted_id_list.append(insert_biosample_model.id)
    return inserted_id_list


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
    delete_project_user_for_transaction(db=db, filters=delete_project_user_filters)
    create_project_user_for_transaction(
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


def admin_project_update_transaction(
    db: Session,
    delete_project_user_filters: List,
    insert_project_user_model_list: List[cellxgene.ProjectUser],
    update_project_filters: List,
    update_project_dict: Dict,
    update_analysis_filters: List,
    update_analysis_dict: Dict,
):
    delete_project_user_for_transaction(db=db, filters=delete_project_user_filters)
    create_project_user_for_transaction(
        db=db, insert_project_user_model_list=insert_project_user_model_list
    )
    update_project_for_transaction(
        db=db, filters=update_project_filters, update_dict=update_project_dict
    )
    update_analysis_for_transaction(
        db=db, filters=update_analysis_filters, update_dict=update_analysis_dict
    )
    db.commit()


def get_species_list(db: Session, query_list: List, filters: List | None):
    return db.query(*query_list).filter(and_(*filters))


def create_gene(db: Session, insert_gene_model_list: List[cellxgene.GeneMeta]):
    db.add_all(insert_gene_model_list)
    db.commit()


def create_taxonomy(
    db: Session, insert_taxonomy_model_list: List[cellxgene.CellTaxonomy]
):
    db.add_all(insert_taxonomy_model_list)
    db.commit()


def create_h5ad(db: Session, insert_h5ad_model: cellxgene.FileLibrary):
    db.add(insert_h5ad_model)
    db.commit()


def create_h5ad_for_transaction(db: Session, insert_h5ad_model: cellxgene.FileLibrary):
    db.add(insert_h5ad_model)


def get_h5ad(db: Session, filters: List | None):
    return db.query(cellxgene.FileLibrary).filter(and_(*filters))


def update_upload_file(
    db: Session,
    update_project_filters: List,
    update_project_dict: Dict,
    update_biosample_filters: List,
    update_biosample_dict: Dict,
):
    update_project_for_transaction(
        db=db, filters=update_project_filters, update_dict=update_project_dict
    )
    update_biosample_for_transaction(
        db=db, filters=update_biosample_filters, update_dict=update_biosample_dict
    )
    db.commit()


def create_cell_taxonomy_relation(
    db: Session, insert_model_list: List[cellxgene.CellTaxonomyRelation]
):
    db.add_all(insert_model_list)
    db.commit()


def get_cell_taxonomy_relation(db: Session, query_list: List, filters: List):
    return db.query(*query_list).filter(and_(*filters))


def get_pathway_score(db: Session, filters: List):
    return db.query(cellxgene.PathwayScore).filter(and_(*filters))


def get_cell_taxonomy_relation_test1(db: Session, query_list: List, filters: List):
    print(1111)
    hierarchy = (
        db.query(cellxgene.CellTaxonomyRelation, literal(0).label("level"))
        .filter(and_(*filters))
        .cte(name="hierarchy", recursive=True)
    )

    parent = aliased(hierarchy, name="p")
    print(hierarchy)
    children = aliased(cellxgene.CellTaxonomyRelation, name="c")
    hierarchy = hierarchy.union_all(
        db.query(children, (parent.c.level + 1).label("level")).filter(
            children.cl_pid == parent.c.cl_id
        )
    )

    result = (
        db.query(cellxgene.CellTaxonomyRelation, hierarchy.c.level)
        .select_from(hierarchy)
        .all()
    )
    print(result)
    return result


def get_cell_test2(db: Session):
    from sqlalchemy.sql import select, union_all

    # class Employee(Base):
    #     __tablename__ = 'employees'
    #     id = Column(Integer, primary_key=True)
    #     name = Column(String)
    #     manager_id = Column(Integer, ForeignKey('employees.id'))
    #     manager = relationship('Employee', remote_side=[id])

    # Define the recursive query using CTE
    print("start")
    cte = db.query(
        cellxgene.CellTaxonomyRelation.cl_id.label("child_id"),
        cellxgene.CellTaxonomyRelation.name.label("name"),
        cellxgene.CellTaxonomyRelation.cl_pid.label("parent_id"),
    ).filter(cellxgene.CellTaxonomyRelation.cl_id.in_(['CL:0000007','CL:0000208','CL:0002288','CL:0002321','CL:0000312','CL:0000114','CL:0002645','CL:0000360','CL:0000372','CL:0000008','CL:0000133','CL:1000083','CL:0000216','CL:1001606','CL:0002561','CL:0000192','CL:0002160','CL:0002562','CL:0000353','CL:0000441','CL:0000312','CL:0002161','CL:0005026','CL:0011010','CL:0010000','CL:0002484','CL:0000365','CL:0000854','CL:0002153','CL:0002148','CL:0005022','CL:1000448','CL:0002190','CL:0000223','CL:0002170','CL:0000066','CL:0000066','CL:0002451','CL:0011012','CL:0000222','CL:0000237','CL:0000362','CL:0002135','CL:0002285','CL:2000033','CL:0000238','CL:0000419','CL:2000073','CL:0002640','CL:0007018','CL:0002638','CL:0002560','CL:0002664','CL:0002308','CL:0002189','CL:0002655','CL:0002159','CL:0000032','CL:2000081','CL:0000374','CL:1000447','CL:1000085','CL:1000348','CL:0000649','CL:0000712','CL:2000082','CL:0002337','CL:0011011','CL:0002158','CL:0002351','CL:0000357','CL:0002418','CL:2000075','CL:0000221','CL:0002187','CL:0002283','CL:0000185','CL:0007006','CL:0002654','CL:0002643','CL:0000499','CL:1000486','CL:0000240','CL:0002221','CL:0000011','CL:0007020','CL:0002483','CL:0000646','CL:2000092','CL:0000036','CL:0000361','CL:1000428','CL:0002607','CL:2000000','CL:0000646','CL:0000646','CL:0000185','CL:0000077','CL:0000312','CL:0000646','CL:0000646']
                                                      )).cte(recursive=True)
    cte_alias = aliased(cte, name="e")

    cte = cte.union_all(
        select(
            cellxgene.CellTaxonomyRelation.cl_id,
            cellxgene.CellTaxonomyRelation.name,
            cellxgene.CellTaxonomyRelation.cl_pid,
            # cellxgene.CellTaxonomyRelation
        ).where(cellxgene.CellTaxonomyRelation.cl_id == cte_alias.c.parent_id)
    )

    # Execute the recursive query
    result = db.query(cte).all()
    print(result)
    cl_id_list = []
    # Print the result
    for row in result:
        if row.child_id not in cl_id_list:
            cl_id_list.append(row.child_id)
    print(cl_id_list)
    taxonomy_list = []
    #     print(type(row))
    #     print(row.employee_id, row.employee_name, row.manager_id)


if __name__ == "__main__":
    pass
    from orm.dependencies import get_db
    get_cell_test2(db=next(get_db()))
    # create_project_biosample(db=next(get_db()))
    # update_project_biosample(db=next(get_db()))
    # delete_project_biosample(db=next(get_db()))
    # add_project_biosample_relation(db=next(get_db()))
    # delete_project_biosample_relation(db=next(get_db()))
    # update_project_biosample_relation(db=next(get_db()))
    # res = get_user(db=next(get_db()), filters=[cellxgene.User.email_address == '619589351@qq.com'])
    # print(res)
    # print(res.first().id)
